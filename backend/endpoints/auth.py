from fastapi import APIRouter, Request, status

from starlette.config import Config
from fastapi.responses import RedirectResponse, JSONResponse

from authlib.integrations.starlette_client import OAuth

from database.utils.user import get_user, update_user, create_user
from models.users import User

router = APIRouter(tags=["Google Authentication"])

config = Config('.env')
oauth = OAuth(config)
CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@router.get('/login')
async def login(request: Request):
    # Redirect Google OAuth back to our application
    redirect_uri = request.url_for('auth')

    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.route('/auth')
async def auth(request: Request):
    # Perform Google OAuth
    token = await oauth.google.authorize_access_token(request)
    req_user = await oauth.google.parse_id_token(request, token)
    db = request.app.state.db
    user = await get_user(db, req_user['email'])
    if user is None:
        # Creates a new user in the database
        user = User(**{'first_name': req_user['given_name'],
                       'last_name': req_user['family_name'],
                       'email': req_user['email'],
                       'avatar_url': req_user['picture']})
        await create_user(db, user)
    else:
        # Updates name and profile picture in the database if changed
        user.first_name = req_user['given_name']
        user.last_name = req_user['family_name']
        user.avatar_url = req_user['picture']
        await update_user(db, user)

    request.session['user'] = dict(user)

    return RedirectResponse(url='http://127.0.0.1:8080')


@router.get('/logout')  # Tag it as "authentication" for our docs
async def logout(request: Request):
    # Remove the user
    request.session.pop('user', None)
    return RedirectResponse(url='/')


@router.get('/current-user')
async def get_current_user(request: Request):
    user_data = request.session.get('user')
    if user_data is not None:
        user = User(**user_data)
        return user
    else:
        return JSONResponse({'None': 'No user is authenticated'}, status_code=status.HTTP_404_NOT_FOUND)
