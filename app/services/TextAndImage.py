#This template will work in a such a way that, it would optioanlly accept page_id as an input, here the main job would be patch the content dynamically(i.e whether one/two column(s)), here only modifcation of the page is considered as an development & not the creation of the page(for that, the approach would be different).
#Also it would be kept in mind that this particular file/function could be called recursively for multiple pages having page_type as contentPage & optionally list of page_ids could also be accepted as an argument.

import asyncio
from openai import OpenAI
from app.core.config import get_settings
import json
import xml.etree.ElementTree as ET
import time


class TextAndImage_Template:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY)  

    def textAndImageCounter(self):    
        #pre-requisite to count number of columns in the page i.e 1 or 2
        target_page_id = "1385907942298101467"
        tree = ET.parse('output.xml')
        root = tree.getroot()
        # Namespace handling (if required)
        namespace = {'ns': 'http://lrncontent.lrn.com/schema/lcec/lrncourse'}
        ET.register_namespace('', namespace['ns'])  # Register default namespace
        # Find the <page> tag with the specific pageid
        page = root.find(f".//ns:page[@pageid='{target_page_id}']", namespace)
        # Count <text> tag(s) under this page
        if page is not None:
            text_and_image_column = page.findall('.//ns:text',namespace)
            print("************************************")
            print("count of columns present in course is",len(text_and_image_column))
            print("************************************")
            return len(text_and_image_column)

    def xml_manipulation(self, text_and_image_content):
        try:
            print("printing list length")
            print("************************************")
            print("No. of paragrpahs is : " ,len(text_and_image_content['text_and_image_template_content']))
            print("************************************")
            #pre-requisite to count number of columns in the page i.e 1 or 2
            target_page_id = "1385907942298101467"
            tree = ET.parse('output.xml')
            root = tree.getroot()
            # Namespace handling (if required)
            namespace = {'ns': 'http://lrncontent.lrn.com/schema/lcec/lrncourse'}
            ET.register_namespace('', namespace['ns'])  # Register default namespace
            # Find the <page> tag with the specific pageid
            page = root.find(f".//ns:page[@pageid='{target_page_id}']", namespace)
            page_title_element = page.find(".//ns:title", namespace)
            page_title_element.text = text_and_image_content['text_and_image_template_title']
            if page is not None:
                for i, item in enumerate(page.findall(".//ns:text", namespace)):
                    if i < len(text_and_image_content['text_and_image_template_content']):  # Ensure we don't exceed dictionary entries
                        column_content = text_and_image_content['text_and_image_template_content'][i]
                        content_element = item.find(".//ns:p", namespace)
                        if content_element is not None:
                            # Clear all content inside the outermost <p> tag
                            content_element.clear()
                        content_element.text = column_content
                # Write the modified XML back to file
            tree.write('output.xml', encoding='utf-8', xml_declaration=True)

        except Exception as e:
            raise Exception(f"Error in xml manipulation for TextAndImage template: {str(e)}")     
        

    async def textAndImageGenerator(self):
        try:
            column_count = self.textAndImageCounter()
            course_topic_area = "Ethics in the Workplace"
            industry = "Hospitality"
            text_and_image_function = {
                "name" : "generate_text_and_image_content",
                "description": "Generates content for a Text And Image template",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text_and_image_template_title": {
                            "type": "string",
                            "description": "The title of the Text And Image template"
                        },
                        "text_and_image_template_content": {
                            "type": "array",
                            "description": "A list of paragraph(s) for the Text And Image template",
                            "items": {
                                "type": "string",
                                "description": "A paragraph of content"
                            }
                        }
                    },
                    "required": ["text_and_image_template_title", "text_and_image_template_content"]
                }
            }
            system_prompt = "You are a Course Creation Agent at a popular online learning platform. Your role is to assist customers who are interested in creating courses on the platform. You have extensive knowledge of the course creation process and are familiar with the platform's guidelines and requirements. Your goal is to provide helpful and accurate information to customers, addressing their inquiries and guiding them through the course creation process.  You are now tasked with generating content for a Text And Image template. The industry, course topic area, and the number of paragraphs will be provided dynamically."

            user_prompt = f"""
            Generate content for a Text And Image template for a course on {course_topic_area} in the {industry} industry. The template should include {column_count} paragraphs. Each paragraph should be engaging, informative, and relevant to the course topic area and industry.

            Please generate the content in the following format:
            {{
                "text_and_image_template_title": "Title from LLM",
                "text_and_image_template_content": [
                    "Paragraph 1",
                    "Paragraph 2",
                    ...
                ]
            }}
            """

            # Log the start time
            start_time = time.time()
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                functions=[text_and_image_function],  # Add the function definition
                function_call={"name": "generate_text_and_image_content"}  # Force calling the function
            )
            text_and_image_content = json.loads(response.choices[0].message.function_call.arguments)  # this is a dictionary
            print(text_and_image_content)
            # Log the end time
            end_time = time.time()
            # Calculate the time taken
            time_taken = end_time - start_time
            print(f"Time taken for OpenAI LLM call for Text&Image template content generation: {time_taken} seconds")
            self.xml_manipulation(text_and_image_content)

        except Exception as e:
            raise Exception(f"Error in Text&Image's main function: {str(e)}")
