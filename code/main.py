from fastapi.responses import HTMLResponse, RedirectResponse, Response
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from urllib.parse import urljoin
import requests
import secrets
import string
import base64
import time
import os

# MLflow tracking URI and API URL from environment variables
MLFLOW_TRACKING_URI = os.environ['MLFLOW_TRACKING_URI']
API_URL = os.environ['API_URL']

# Generate a secret key for session middleware
SECRET_KEY = ''.join([secrets.choice(string.ascii_letters) for _ in range(32)])

# Timeout in seconds
INACTIVITY_TIMEOUT = os.getenv('INACTIVITY_TIMEOUT')
if INACTIVITY_TIMEOUT:
    INACTIVITY_TIMEOUT = int(INACTIVITY_TIMEOUT)
else:
    # Default value of 30 minutes if not otherwise provided
    INACTIVITY_TIMEOUT = 30 * 60

# Instantiate the app, add session middleware, templates, and mount the static files
app = FastAPI(docs_url=None, redoc_url=None)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')

# Function to authenticate


def authenticate(username: str, password: str):
    '''
    Authenticate a user

    Parameters
    ----------
    username: str
        The username
    password: str
        The password

    Returns
    -------
    authenticated: bool
        Whether authenticated or not
    '''
    with requests.Session() as sess:
        resp = sess.post(
            f'{API_URL}/password/verify',
            json={
                'username': username,
                'password': password
            }
        )
    if resp.ok:
        return True


# Function to check for inactivity
def check_inactivity(request: Request):
    '''
    Check for inactivity based on request

    Returns
    -------
    is_ok: bool
        Returns True if not timed out, False if timed out
    '''
    last_active = request.session.get('last_active', None)
    if last_active:
        if time.time() - last_active > INACTIVITY_TIMEOUT:
            request.session.clear()
            return False
    request.session['last_active'] = time.time()
    return True


@app.get('/login', response_class=HTMLResponse)
async def login_form(request: Request):
    '''Login page'''
    return templates.TemplateResponse(name = 'login.html', context = {'request': request})


@app.post('/login')
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    '''Login POST endpoint'''

    # Attempt to authenticate - if successful, go to home page
    if authenticate(username, password):
        request.session['user'] = username
        request.session['last_active'] = time.time()
        return RedirectResponse(url='/', status_code=302)

    # Authentication not successful, tell user
    return templates.TemplateResponse(name = 'login.html', context = {'request': request, 'error': 'Invalid credentials'})


@app.get('/logout')
async def logout(request: Request):
    '''Logout page'''

    # Clear the session
    request.session.clear()

    # Go back to login page
    return RedirectResponse(url='/login')


@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    '''Home page'''

    # Always check for authentication and session
    if 'user' not in request.session or not check_inactivity(request):
        return RedirectResponse(url='/login')

    # Return home page template
    return templates.TemplateResponse(name = 'home.html', context = {'request': request})


@app.api_route('/mlflow/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE'])
async def proxy_mlflow(path: str, request: Request):
    '''Page for proxying MLflow (both API and UI pages)'''

    # Check if the user is authenticated via session
    user = request.session.get('user')

    # If not authenticated via session, try basic auth (API)
    if not user:

        # Attempt to get credentials from Basic Auth header
        auth = request.headers.get('Authorization')

        if auth and auth.startswith('Basic '):

            # Decode the credentials from base64
            auth_str = auth[len('Basic '):]
            try:
                decoded = base64.b64decode(auth_str).decode('utf-8')
                username, password = decoded.split(':', 1)
            except Exception:
                raise HTTPException(401, 'Unauthenticated')

            # Attempt to authenticate using the provided username and password
            if not authenticate(username, password):
                raise HTTPException(401, 'Unauthenticated')

            # Success
            user = username
        else:
            return RedirectResponse(url='/login')

    # Session is valid or basic authentication is successful
    with requests.Session() as sess:
        resp = sess.get(f'{API_URL}/users/role/{user}')
    role = resp.json()

    # If role is not admin or data scientist, user can't access
    if role not in ['admin', 'data_scientist']:
        return RedirectResponse(url='/login')

    # Get the URI and the query
    mlflow_url = urljoin(MLFLOW_TRACKING_URI, path)
    query_string = request.url.query

    # Proxy request to MLflow service
    response = requests.request(
        method=request.method,
        url=mlflow_url,
        headers={key: value for (key, value)
                 in request.headers.items() if key != 'Host'},
        params=query_string,
        data=await request.body(),
        cookies=request.cookies,
        allow_redirects=False,
    )

    # Get the response
    client_response = Response(
        content=response.content,
        status_code=response.status_code,
        headers={key: value for key, value in response.headers.items()
                 if key.lower() != 'transfer-encoding'}
    )

    # Return the response
    return client_response


@app.get('/users', response_class=HTMLResponse)
async def user_settings(request: Request):
    '''User settings page'''

    # Always check for session
    if 'user' not in request.session or not check_inactivity(request):
        return RedirectResponse(url='/login')

    # Return the user management page
    return templates.TemplateResponse(name = 'user_management.html', context = {'request': request})


@app.get('/models', response_class=HTMLResponse)
async def list_models(request: Request):
    '''Models page'''

    # Always check for session
    if 'user' not in request.session or not check_inactivity(request):
        return RedirectResponse(url='/login')

    # Return the models page
    return templates.TemplateResponse(name = 'list_models.html', context = {'request': request})


@app.get('/variables', response_class=HTMLResponse)
async def manage_variables(request: Request):
    '''Manage variables page'''

    # Always check for session
    if 'user' not in request.session or not check_inactivity(request):
        return RedirectResponse(url='/login')

    # Return the variables page
    return templates.TemplateResponse('manage_variables.html', {'request': request})
