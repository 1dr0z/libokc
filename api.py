from libokc.errors import AuthenticationError
from time import clock
import libokc.parse as parse
import requests


class Session(requests.Session):
    def __init__(self, delay=3):
        super().__init__()
        self.delay = delay
        self.timestamp = -delay

    def get_request(self, method, url, data=None, headers=None, cookies=None):
        req_options = {
            'method': method.upper(),
            'url': url,
        }

        if data is not None:
            if method.upper() == 'GET':
                req_options['params'] = data
            else:
                req_options['data'] = data

        if headers is not None:
            req_options['headers'] = headers

        if cookies is not None:
            req_options['cookies'] = cookies

        request = requests.Request(**req_options)
        return self.prepare_request(request)

    def send(self, request, **kwargs):
        """
        Add a delay to all requests so we're not spamming okcupid servers.
        Raise exception on unsuccessul status
        """
        while clock() - self.timestamp < self.delay:
            pass

        self.timestamp = clock()
        response = super().send(request, **kwargs)
        response.raise_for_status()
        return response


class Profile(object):
    def __init__(self, session, name, userid=None, age=None,
                 location=None, match=None, rating=None,
                 gender=None, favorite=None):
        self._session = session
        self._id = userid
        self._name = name
        self._age = age
        self._location = location
        self._match = match
        self._rating = rating
        self._gender = gender
        self._favorite = favorite
        self._questions = parse.Questions(self)

    ## TODO: If the below properties are not set at the time they are accessed, populate all basic profile data
    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def age(self):
        return self._age

    @property
    def location(self):
        return self._location

    @property
    def match(self):
        return self._match

    @property
    def rating(self):
        return self._rating

    @property
    def gender(self):
        return self._gender

    @property
    def is_favorite(self):
        return self._favorite

    def questions(self, **kwargs):
        return (Question(**data) for data in self._questions.iter(**kwargs))

    def __str__(self):
        return '<Profile of {0}>'.format(self._name)


class User(Profile):
    def __init__(self, username, password, session=None, log_in=True):
        if session is None:
            session = Session()

        super().__init__(session, username)

        self._session = session
        self._username = username
        self._password = password
        self._favorites = parse.Favorites(self)

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

    def favorites(self, **kwargs):
        return (Profile(self._session, **data) for data in self._favorites.iter(**kwargs))

    def __str__(self):
        return '<User {0}>'.format(self._username)


class Question(object):
    def __init__(self, id, text=None, answered=None, public=None,
                 answer_target=None, explanation_target=None, acceptable_target=None,
                 answer_viewer=None, explanation_viewer=None, acceptable_viewer=None):
        self._id   = id
        self._text = text
        self._answered = answered
        self._public   = public
        self._t_answer = answer_target
        self._v_answer = answer_viewer
        self._t_note   = explanation_target
        self._v_note   = explanation_viewer
        self._t_accepted = acceptable_target
        self._v_accepted = acceptable_viewer

    ## TODO: find a way to determine the below properties in case they aren't set

    @property
    def id(self):
        return self._id

    @property
    def text(self):
        return self._text

    @property
    def answered(self):
        return self._answered

    @property
    def public(self):
        return self._public

    @property
    def answer_target(self):
        return self._t_answer

    @property
    def answer_viewer(self):
        return self._v_answer

    @property
    def accepted_target(self):
        return self._t_accepted

    @property
    def accepted_viewer(self):
        return self._v_accepted

    @property
    def explanation_target(self):
        return self._t_note

    @property
    def explanation_viewer(self):
        return self._v_note

    def __str__(self):
        return '<Question {0}>'.format(self._id)