from openai import OpenAI
from app.core.config import get_settings
import xml.etree.ElementTree as ET

class videoSlideShow_Template():
        def __init__(self):
            self.settings = get_settings()
            self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY) 

        async def videoSlideShowGenerator(self, llm_response):
            try:
                target_page_id = "1337985907539425274"
                tree = ET.parse('course.xml')
                root = tree.getroot()

                # Namespace handling (if required)
                namespace = {'ns': 'http://lrncontent.lrn.com/schema/lcec/lrncourse'}
                ET.register_namespace('', namespace['ns'])  # Register default namespace

                # Find the first <page> tag and its <title> child under that tag
                first_page = root.find(f".//ns:page[@pageid='{target_page_id}']", namespace)
                if first_page is not None:
                    # Update <title> content under the first <page>
                    title_tag = first_page.find('ns:title', namespace)
                    if title_tag is not None:
                        title_tag.text = llm_response[0]  # Replace with the new title

                    # Find <p> inside the <text> tag within the same <page>
                    text_tag = first_page.find('ns:text/ns:p', namespace)
                    if text_tag is not None:
                        text_tag.text = llm_response[1]  # Replace with the new description

                # Save the modified XML back to a file
                tree.write('output.xml', encoding='UTF-8', xml_declaration=True)

            except Exception as e:
                raise Exception(f"Error in videoSlideShowGenerator's main function: {str(e)}")    