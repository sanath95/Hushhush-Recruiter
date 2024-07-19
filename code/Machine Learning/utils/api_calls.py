from aiohttp import ClientSession
# import requests

class ApiCalls:

    def __init__(self, headers):
        self.headers = headers

    async def async_http_get_call(self, url):
        async with ClientSession(headers = self.headers) as session:
            async with session.get(url) as response:
                response_body = await response.json(content_type=None)
                response_headers = response.headers
                response_status_code = response.status
                
        return response_status_code, response_headers, response_body
    
    # we may need this in the future

    # def sync_http_get_call(self, url):
    #     response = requests.get(url=url, headers = self.headers)

    #     return response.status_code, response.headers, response.json()