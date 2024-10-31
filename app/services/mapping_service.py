from typing import List, Dict, Any
import xml.etree.ElementTree as ET

class DataMapper:
    def map_and_modify(self, llm_response: Any) :
        print(llm_response[0], llm_response[1])
        """
        Map data from XML and LLM response, modify XML accordingly
        """
        try:
            tree = ET.parse('course.xml')
            root = tree.getroot()

            # Namespace handling (if required)
            namespace = {'ns': 'http://lrncontent.lrn.com/schema/lcec/lrncourse'}
            ET.register_namespace('', namespace['ns'])  # Register default namespace

            # Find the first <page> tag and its <title> child under that tag
            first_page = root.find('.//ns:page', namespace)
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

            # Add your mapping and XML modification logic here
            # This is a placeholder implementation
            
            # Return the modified XML as string
            return ""  # Replace with actual modified XML
        except Exception as e:
            raise Exception(f"Error in data mapping: {str(e)}")