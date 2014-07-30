from time import clock
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