from libokc.api.session import Session
from libokc.api.errors import AuthenticationError
from .favorites import Favorites


class User(object):
    def __init__(self, username, password, session=None, log_in=True):
        if session is None:
            session = Session()

        self._session = session
        self._username = username
        self._password = password
        self._favorites = Favorites(session)

        if log_in:
            self.login()

    def login(self):
        credentials = {'username': self._username, 'password': self._password}
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36'
        }

        response = self._session.post('https://www.okcupid.com/login', data=credentials, headers=headers)
        if response.url == 'https://www.okcupid.com/login':
            raise AuthenticationError('Could not log in with the credentials provided')

    def favorites(self, *args, **kwargs):
        return self._favorites.iter(*args, **kwargs)