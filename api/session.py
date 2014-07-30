from time import clock
import requests


class Session(requests.Session):
    def __init__(self, delay=3):
        super().__init__()
        self.delay = delay
        self.timestamp = -delay

    def post(self, *args, **kwargs):
        while clock() - self.timestamp < self.delay:
            pass

        self.timestamp = clock()
        response = super().post(*args, **kwargs)
        response.raise_for_status()
        return response

    def get(self, *args, **kwargs):
        while clock() - self.timestamp < self.delay:
            pass

        self.timestamp = clock()
        response = super().get(*args, **kwargs)
        response.raise_for_status()
        return response

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

    # def send(self, request, **kwargs):
    #     print('request:', request.url)
    #     response = super().send(request, **kwargs)
    #     print('response:', response.url)
    #     return response