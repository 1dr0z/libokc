from lxml import html
from urllib.parse import parse_qs, urlparse


class BasePaginated(object):
    def __init__(self, session):
        self.session = session
        self.url     = None

    def get_request(self, url, **kwargs):
        return self.session.get_request('GET', url, data=kwargs)

    def get_html(self, request):
        response = self.session.send(request)
        return response.content.decode('utf8')

    def get_tree(self, html_string):
        return html.fromstring(html_string)

    def get_next_request(self, tree):
        next_url = self.get_next_page_link(tree)
        query    = urlparse(next_url).query
        params   = parse_qs(query, keep_blank_values=True)
        return self.get_request(self.url, **params)

    def get_next_page_link(self, tree):
        raise NotImplementedError()

    def has_next_page(self, tree):
        raise NotImplementedError()

    def iter_element(self, tree):
        raise NotImplementedError()

    def parse_element(self, element):
        raise NotImplementedError()

    def iter(self, **kwargs):
        request = self.get_request(self.url, data=kwargs)

        while True:
            # Get list of user elements from page
            source = self.get_html(request)
            tree = self.get_tree(source)
            elements = self.iter_element(tree)

            # Iterate over user elements
            for element in elements:
                yield self.parse_element(element)

            # Stop iteration when we're out of pages
            if not self.has_next_page(tree):
                break

            request = self.get_next_request(tree)