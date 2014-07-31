from urllib.parse import parse_qs, urlparse
from lxml import html
import re


class Page(object):
    """Basic page functionality"""

    def __init__(self, session, url):
        self._session = session
        self._url     = url

    def get_request(self, **kwargs):
        """Get a PreparedRequest object"""
        return self._session.get_request('GET', self._url, data=kwargs)

    def get_response(self, request):
        """Send a PreparedRequest object and return the response"""
        return self._session.send(request)

    def get_html(self, response):
        """Get the html source of from a response object"""
        return response.content.decode('utf8')

    def get_element(self, html_string):
        """Get an HtmlElement instance from an html string"""
        return html.fromstring(html_string)

    def get_element_from_request(self, request):
        """Get an HTMLElement by sending a request"""
        res = self.get_response(request)
        src = self.get_html(res)
        return self.get_element(src)

    ##

    def find_by_class(self, element, class_name):
        """Find all sub-elements with class_name"""
        return [elem for elem in element.xpath(".//*[@class]")
                if self.element_has_class(elem, class_name)][0]

    def find_by_id(self, element, elem_id):
        """Find the sub-element with elem_id"""
        return element.xpath(".//*[contains(@id, '{0}')]".format(elem_id))[0]

    def find_by_tag(self, element, tag_name):
        """Find all sub-elements by tag_name"""
        return element.xpath(".//{0}".format(tag_name))

    def element_has_class(self, element, class_name):
        """Check whether element has a given class"""
        return re.match(r'\b{0}\b'.format(class_name), self.element_get_attr(element, 'class', ''))

    def element_get_attr(self, element, attribute, default=None):
        """Get an attribute value from an element"""
        return element.attrib.get(attribute, default)


class PaginatedPage(Page):
    """Like a Page object with some methods to work with pagination"""
    def get_next_request(self, element):
        """Get a PreparedRequest object for the next page"""
        next_url = self.get_next_page_link(element)
        if next_url:
            query    = urlparse(next_url).query
            params   = parse_qs(query, keep_blank_values=True)
            return self.get_request(**params)

    def get_next_page_btn(self, element):
        """Get the element for the next page button"""
        return self.find_by_class(self.find_by_class(element, 'pages')[0], 'next')[0]

    def get_next_page_link(self, element):
        """Get the link to the next page"""
        try:
            next_btn = self.get_next_page_btn(element)
            return self.element_get_attr(next_btn, 'href')
        except IndexError:
            return None

    def has_next_page(self, element):
        """Determine whether there is a next page"""
        try:
            next_btn = self.get_next_page_btn(element)
            return not self.element_has_class(next_btn, 'disabled')
        except IndexError:
            return False


class Favorites(PaginatedPage):
    def __init__(self, session):
        super().__init__(session, 'https://www.okcupid.com/favorites')

    def iter_favorite_elements(self, element):
        """Iterate over all favorite elements"""
        return (elem for elem in self.find_by_tag(element, 'div')
                if self.element_has_class(elem, 'user_row_item'))

    def parse_favorite(self, element):
        """Parse a favorite element into useful data"""
        profile_info  = self.find_by_class(element, 'profile_info')
        fave_name     = self.find_by_class(profile_info, 'name').text
        fave_age      = self.find_by_class(profile_info, 'age').text
        fave_location = self.find_by_class(profile_info, 'location').text

        id_raw  = self.element_get_attr(self.find_by_class(element, 'star-rating'), 'id')
        fave_id = id_raw.replace('user_row_rating_', '')

        rating_raw  = self.element_get_attr(self.find_by_class(element, 'current-rating'), 'style')
        rating_re   = re.match(r'[Ww]idth\s?:\s?(\d+)%', rating_raw).group(1)
        fave_rating = 5 * (float(rating_re) / 100)

        match_raw  = self.find_by_class(element, 'percentage').text
        fave_match = match_raw.replace('%', '')

        gender_raw = element.xpath(".//input[@data-gender]/@data-gender")[0]
        fave_gender = {'1': 'M', '2': 'F'}[gender_raw]

        return {
            'userid': fave_id,
            'name': fave_name,
            'age': int(fave_age),
            'location': fave_location,
            'rating': fave_rating,
            'match': float(fave_match),
            'gender': fave_gender,
            'favorite': True,
        }

    def iter(self, **kwargs):
        """Iterate over all favorites, request new pages as needed"""
        request = self.get_request(**kwargs)
        while True:
            # Get list of user elements from page
            page_elem = self.get_element_from_request(request)
            favorites = self.iter_favorite_elements(page_elem)

            # Iterate over favorites
            for favorite in favorites:
                yield self.parse_favorite(favorite)

            # Stop iteration when we're out of pages
            if not self.has_next_page(page_elem):
                break

            request = self.get_next_request(page_elem)
            if not request:
                break