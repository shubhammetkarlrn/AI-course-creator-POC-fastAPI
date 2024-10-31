import xml.etree.ElementTree as ET
from typing import List, Dict
import re

class XMLProcessor:
    def strip_namespace(self, xml_content):
        """Removes namespaces from the XML content."""
        return re.sub(r'\sxmlns(:\w+)?="[^"]+"', '', xml_content, count=0)
    
    def remove_namespace_prefix(self, xml_content):
        """Remove all namespace prefixes from tags in the XML content."""
        xml_content = re.sub(r'<(\w+):(\w+)', r'<\2', xml_content)  # Remove namespace prefixes from opening tags
        xml_content = re.sub(r'</(\w+):(\w+)', r'</\2', xml_content)  # Remove namespace prefixes from closing tags
        return xml_content

    def extract_data(self) -> List[Dict]:
        """
        Extract specific data from XML file and return as list of objects
        """
        try:
            tree = ET.parse('course.xml')
            root = tree.getroot()
            # Namespace used in the XML to handle prefixed tags properly
            namespaces = {
                'ns': 'http://lrncontent.lrn.com/schema/lcec/lrncourse'
            }
            extracted_data = []
            # Iterate through all <topic> tags found in the XML
            for topic in root.findall('ns:topic', namespaces):
                topic_data = ET.tostring(topic, encoding='unicode')
                topic_data = self.strip_namespace(topic_data)
                topic_data = self.remove_namespace_prefix(topic_data)
                extracted_data.append({'topic_data': topic_data})

            return extracted_data[0]['topic_data']
        except Exception as e:
            raise Exception(f"Error processing XML: {str(e)}")
