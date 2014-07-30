import libokc.parse.favorites as parse
from libokc.api.profile import Profile


class Favorites(object):
    def __init__(self, session):
        self._session = session
        self._parser  = parse.Favorites(session)

    def iter(self, low=1):
        while True:
            # Get list of user elements from page
            request = self._parser.get_request(low)
            source = self._parser.get_html(request)
            tree = self._parser.get_element(source)
            favorites = self._parser.iter_favorites(tree)

            # Iterate over user elements
            for favorite in favorites:
                low += 1  # Update 'low' index with each favorite
                yield Profile(**self._parser.parse_favorite(favorite))

            # Stop iteration when we're out of pages
            if not self._parser.has_next_page(tree):
                break