import re
from itertools import filterfalse
from lxml import html


class Favorites(object):
    def __init__(self, session):
        self.session = session

    def get_request(self, low=1):
        """
        Get a prepared request object.  This makes it possible to
        modify the request.
        Parameters
        ---------
        low: int
          favorites offset.
        Returns
        ---------
        PreparedRequest
          Prepared request object ready for modification
        """
        url = 'https://www.okcupid.com/favorites'
        data = {'low': low}
        return self.session.get_request('GET', url, data=data)

    def get_html(self, request):
        """
        Get the HTML response of sending a request
        Parameters
        ---------
        request: PreparedRequest
          Request object to send.
        Returns
        ---------
        string
          HTML response body
        """
        response = self.session.send(request)
        return response.content.decode('utf8')

    def get_element(self, html_string):
        return html.fromstring(html_string)

    def iter_favorites(self, element):
        def not_favorite(x):
            return 'class' not in x.attrib or 'user_row_item' not in x.attrib['class']

        return filterfalse(not_favorite, element.iterfind(".//div[@class='user_list']//div"))

    def has_next_page(self, element):
        """
        :todo check for 'disabled' class on button instead
        """
        return self.get_next_link(element) is not None

    def get_next_link(self, element):
        try:
            return element.xpath(".//*[contains(@class, 'pages')]//*[contains(@class, 'next')]//a/@href")[0]
        except IndexError:
            return None

    def parse_favorite(self, favorite):
        info = favorite.xpath(".//div[@class='profile_info']")[0]
        name = info.xpath(".//*[@class='name']/text()")[0]
        age = info.xpath(".//*[@class='age']/text()")[0]
        location = info.xpath(".//*[@class='location']/text()")[0]

        id_raw = favorite.xpath(".//*[contains(@class, 'star-rating')]/@id")[0]
        id = id_raw.replace('user_row_rating_', '')

        rating_raw = favorite.xpath(".//*[@class='current-rating']/@style")[0]
        rating_re = re.match(r'[Ww]idth\s?:\s?(\d+)%', rating_raw).group(1)
        rating = 5 * (float(rating_re) / 100)

        match_raw = favorite.xpath(".//*[@class='percentage']/text()")[0]
        match = match_raw.replace('%', '')

        gender_raw = favorite.xpath(".//input[@data-gender]/@data-gender")[0]
        gender = {'1': 'M', '2': 'F'}[gender_raw]

        return {
            'userid': id,
            'name': name,
            'age': int(age),
            'location': location,
            'rating': rating,
            'match': float(match),
            'gender': gender,
            'favorite': True
        }