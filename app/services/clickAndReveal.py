from openai import OpenAI
from app.core.config import get_settings
import json
import xml.etree.ElementTree as ET
import time

class ClickAndReveal_Template:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY) 

    def clickAndRevealTagsCounter(self):
        target_page_id = "2336253760955861444"
        tree = ET.parse('output.xml')
        root = tree.getroot()
        print("root is",root)
        # Namespace handling (if required)
        namespace = {'ns': 'http://lrncontent.lrn.com/schema/lcec/lrncourse'}
        ET.register_namespace('', namespace['ns'])  # Register default namespace
    
        # Find the <page> tag with the specific pageid
        page = root.find(f".//ns:page[@pageid='{target_page_id}']", namespace)
        print("targeted page is", page)
    
        # Count <clickAndRevealItem> tags under this page
        if page is not None:
            click_and_reveal_items = page.findall('.//ns:clickAndRevealItem',namespace)
            return len(click_and_reveal_items)    
        
    def xml_manipulation(self, click_and_reveal_content):
        try:
            target_page_id = "2336253760955861444"
            tree = ET.parse('output.xml')
            root = tree.getroot()
            print("root is",root)
            # Namespace handling (if required)
            namespace = {'ns': 'http://lrncontent.lrn.com/schema/lcec/lrncourse'}
            ET.register_namespace('', namespace['ns'])  # Register default namespace
            page = root.find(f".//ns:page[@pageid='{target_page_id}']", namespace)
            if page is not None:
                # Loop through <clickAndRevealItem> tags
                for i, item in enumerate(page.findall(".//ns:clickAndRevealItem", namespace)):
                    print("inside for loop")
                    if i < len(click_and_reveal_content['interactions']):  # Ensure we don't exceed dictionary entries
                        interaction = click_and_reveal_content['interactions'][i]

                        # Update <click> text
                        click_text = item.find("ns:click/ns:text", namespace)
                        if click_text is not None:
                            click_text.text = interaction['title']

                        # Update <reveal> text
                        reveal_text = item.find("ns:reveal/ns:text/ns:p", namespace)
                        if reveal_text is not None:
                            reveal_text.text = interaction['description']

                # Write the modified XML back to file
            tree.write('output.xml', encoding='utf-8', xml_declaration=True)


        except Exception as e:
            raise Exception(f"Error in xml manipulation for clickAndReveal template: {str(e)}")     



    async def clickAndRevealGenerator(self):
        #here we'll generate the click & reveal data content using LLM
        #we'll count the number of interactions present in the XML & pass that count to the LLM
        interaction_count =self.clickAndRevealTagsCounter()
        try:
            course_topic_area = "Ethics in the Workplace"
            industry = "Corporate"
            click_and_reveal_function = {
                "name": "generate_click_and_reveal_content",
                "description": "Generates content for a Click And Reveal interaction template",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "interactions": {
                            "type": "array",
                            "description": "A list of interaction boxes with titles and descriptions",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "The title of the interaction box"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "The description revealed when the box is clicked"
                                    }
                                },
                                "required": ["title", "description"]
                            }
                        }
                    },
                    "required": ["interactions"]
                }
            }
            
            system_prompt = "You are a Course Creation Agent at a popular online learning platform. Your role is to assist customers who are interested in creating courses on the platform. You have extensive knowledge of the course creation process and are familiar with the platform's guidelines and requirements. Your goal is to provide helpful and accurate information to customers, addressing their inquiries and guiding them through the course creation process. You are now tasked with generating multiple-choice questions (MCQs) for a course on ethics in the workplace in hospitality industry."

            user_prompt = f"""
            Generate content for a "Click And Reveal" interaction template for a course on {course_topic_area} in the {industry} industry. The template should include {interaction_count} interaction boxes. Each box should reveal a title and description when clicked. The content should be engaging, informative, and relevant to the course topic area and industry.

            Please generate the content in the following format:
            {{
                "interactions": [
                    {{
                        "title": "Title 1",
                        "description": "Description 1"
                    }},
                    {{
                        "title": "Title 2",
                        "description": "Description 2"
                    }},
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
                functions=[click_and_reveal_function],  # Add the function definition
                function_call={"name": "generate_click_and_reveal_content"}  # Force calling the function
            )
            click_and_reveal_content = json.loads(response.choices[0].message.function_call.arguments)  # this is a dictionary
            print(click_and_reveal_content)
            # Log the end time
            end_time = time.time()
            # Calculate the time taken
            time_taken = end_time - start_time
            print(f"Time taken for OpenAI LLM call for ClickAndReveal Interaction content generation: {time_taken} seconds")

            #here we can have 2 approaches for xml manipulation
                # 1) we can directly patch the generated content into the souce XML on .text
                # 2) or we can create entire new chunk of clickAndRevealItem & patch it into the source XML
                #----------------------------------------------------------------------------------------#
                # 1st approach to be used when existing course is available & 2nd approach to be used when we are creating new course/page/lessson from scratch where attributes such as lessonId, pageId needs to be generated dynamically(database driven)
                # ****** For POC purpose using 1st approach ******** #

            self.xml_manipulation(click_and_reveal_content)    

        except Exception as e:
            raise Exception(f"Error in clickAndRevealGenerator's main function: {str(e)}")    