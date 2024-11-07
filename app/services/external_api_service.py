import httpx
import requests
from app.core.config import get_settings

class ExternalAPIService:
    def __init__(self):
        self.settings = get_settings()
        self.endpoint = self.settings.EXTERNAL_API_ENDPOINT
    
    async def send_xml(self, xml_content: str) -> dict:
        """
        Send modified XML to external API
        """
        try:
             # Read the XML file from the root directory
            with open("output.xml", "rb") as file_stream:
                files = {
                    'file': ('output.xml', file_stream, 'application/xml')
                }
                data = {
                    'systemId': '8241000369',
                    'fileType': 'coursexml'
                }
                headers = {
                    'username-bypass': 'shubham.metkar',
                    'Accept': '*/*'
                }
                 # Send the POST request with form-data
                print("making API call where files is", files)
                response = requests.post(self.endpoint, headers=headers, data=data, files=files)
                print("response is", response)
                # Check if the response is JSON
                if response.headers.get('Content-Type') == 'application/json':
                    return response.json()
                else:
                    return {"status_code": response.status_code, "content": response.text}
                # async with httpx.AsyncClient() as client:
                #     response = await client.post(
                #         self.endpoint,
                #         data=data,
                #         files=files,
                #         headers=headers
                #     )
                #     response.raise_for_status()
                #     return response.json()
        except Exception as e:
            raise Exception(f"Error calling external API: {str(e)}")
