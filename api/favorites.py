import libokc.parse.favorites as parse
from libokc.api.profile import Profile


class Favorites(object):
    def __init__(self, session):
        self._session = session
        self._parser  = parse.Favorites(session)

    def iter(self, low=1):
        return (Profile(**data) for data in self._parser.iter(low=low))