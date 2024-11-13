import asyncio
from openai import OpenAI
from app.core.config import get_settings
import json
import xml.etree.ElementTree as ET
import time

class MCQ_SAQ_Template():
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY)

    def MCQ_Content_Generator(self, options_count, question_type):
        try:
            course_topic_area = "Ethics in the Workplace"
            industry = "Hospitality"
            single_ans_correct_format_function = {
                "name": "generate_single_answer_correct_content",
                "description": "Generates content for a single-answer correct MCQ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scenario_title": {
                            "type": "string",
                            "description": "The title of the scenario"
                        },
                        "scenario_description": {
                            "type": "string",
                            "description": "The description of the scenario"
                        },
                        "question_text": {
                            "type": "string",
                            "description": "The text of the question"
                        },
                        "question_description": {
                            "type": "string",
                            "description": "The description of the question"
                        },
                        "options": {
                            "type": "array",
                            "description": "A list of options for the question",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "option_text": {
                                        "type": "string",
                                        "description": "The text of the option"
                                    },
                                    "is_correct": {
                                        "type": "boolean",
                                        "description": "Indicates if the option is correct"
                                    }
                                },
                                "required": ["option_text", "is_correct"]
                            }
                        }
                    },
                    "required": ["scenario_title", "scenario_description", "question_text", "question_description", "options"]
                }
            }

            prompts = {
            "multipleChoice": {
                "system_prompt": """
                You are a Course Creation Agent at a popular online learning platform for corporate employees. Your role is to assist customers who are interested in creating courses on the platform. You have extensive knowledge of the course creation process and are familiar with the platform's guidelines and requirements. Your goal is to provide helpful and accurate information to customers, addressing their inquiries and guiding them through the course creation process. You are now tasked with generating content for a multiple-choice question (MCQ) where only one answer is correct. The industry, course topic area, and the number of options will be provided dynamically.
                """,
                "user_prompt": f"""
                Generate content for a multiple-choice question (MCQ) for a course on {course_topic_area} in the {industry} industry. The MCQ should have only one correct answer among the given options. The number of options should be {options_count}. Create a brief or detailed scenario using person characters related to the given course topic area and industry. Based on this scenario, create an innovative and slightly complex question with multiple options, among which one would be the correct answer.

                Please generate the content in the following format:
                {{
                    "scenario_title": "Title of the scenario",
                    "scenario_description": "Description of the scenario",
                    "question_text": "Text of the question",
                    "question_description": "Description of the question",
                    "options": [
                        {{
                            "option_text": "Option 1",
                            "is_correct": true/false
                        }},
                        {{
                            "option_text": "Option 2",
                            "is_correct": true/false
                        }},
                        ...
                    ]
                }}
                """
            },
            "checkAll": {
                "system_prompt": """
                You are a Course Creation Agent at a popular online learning platform for corporate employees. Your role is to assist customers who are interested in creating courses on the platform. You have extensive knowledge of the course creation process and are familiar with the platform's guidelines and requirements. Your goal is to provide helpful and accurate information to customers, addressing their inquiries and guiding them through the course creation process. You are now tasked with generating content for a multiple-choice question (MCQ) where more than one answer is correct. The industry, course topic area, and the number of options will be provided dynamically.
                """,
                "user_prompt": f"""
                Generate content for a multiple-choice question (MCQ) for a course on {course_topic_area} in the {industry} industry. The MCQ should have multiple correct answers among the given options. The number of options should be {options_count}. Create a brief or detailed scenario using person characters related to the given course topic area and industry. Based on this scenario, create an innovative and slightly complex question with multiple options, among which more than one would be the correct answers.

                Please generate the content in the following format:
                {{
                    "scenario_title": "Title of the scenario",
                    "scenario_description": "Description of the scenario",
                    "question_text": "Text of the question",
                    "question_description": "Description of the question",
                    "options": [
                        {{
                            "option_text": "Option 1",
                            "is_correct": true/false
                        }},
                        {{
                            "option_text": "Option 2",
                            "is_correct": true/false
                        }},
                        ...
                    ]
                }}
                """
            }
        }
            
            system_prompt = prompts[question_type]["system_prompt"]
            user_prompt = prompts[question_type]["user_prompt"]

            # Log the start time
            start_time = time.time()
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                functions=[single_ans_correct_format_function],  # Add the function definition
                function_call={"name": "generate_single_answer_correct_content"}  # Force calling the function
            )
            content = json.loads(response.choices[0].message.function_call.arguments)  # this is a dictionary
            # print(content)
            print("**********************************************")
            # Log the end time
            end_time = time.time()
            # Calculate the time taken
            time_taken = end_time - start_time
            print(f"Time taken for OpenAI LLM call for MCQ template content generation: {time_taken} seconds")
            return content
        except Exception as e:
            raise Exception(f"Error calling OpenAI API for function MCQ_Content_Generator(): {str(e)}")     

    def xml_manipulator(self,llm_response):
        try:
            target_page_id = "2010546873082608811"
            tree = ET.parse('output.xml')
            root = tree.getroot()
            # Namespace handling (if required)
            namespace = {'ns': 'http://lrncontent.lrn.com/schema/lcec/lrncourse'}
            ET.register_namespace('', namespace['ns'])  # Register default namespace
            # Find the <page> tag with the specific pageid
            page = root.find(f".//ns:page[@pageid='{target_page_id}']", namespace)
            question_element = page.find(".//ns:question", namespace)

            scenario_title = page.find(".//ns:title", namespace)
            scenario_title.text = llm_response['scenario_title']

            scenario_desc = page.find("ns:text/ns:p", namespace)
            scenario_desc.text = llm_response['scenario_description']

            question_title = question_element.find(".//ns:questionText", namespace)
            question_title.text = llm_response['question_text']

            question_desc = question_element.find(".//ns:questionDescription", namespace)
            question_desc.text = llm_response['question_description']
            for index, option_pair in enumerate(llm_response['options']):
                option_element = question_element.find(f".//ns:choice[{index+1}]", namespace)
                option_element_text = option_element.find(".//ns:p", namespace)
                option_element_text.text = option_pair['option_text']
                if option_pair['is_correct'] == True:
                    option_element.attrib['isCorrect'] = 'true'
                else:
                    option_element.attrib['isCorrect'] = 'false'
            tree.write('output.xml', encoding='utf-8', xml_declaration=True)            

        except Exception as e:
            raise Exception(f"Unable to manipulate XML for MCQ template of page_id : {target_page_id}: {str(e)}")     
        

    async def MCQ_SAQ_Generator(self):
        #stages (approach considered keeping in mind about course modification & not course creation from scratch):
        # stage_1 = "Check whether question type is multipleChoice(only one answer correct) or checkAll(more than one answer correct) "
        # stage_2 = "Check the count of <choices> (i.e options) tags under <question> tag"
        # stage_3 = "Based on the above stages, create a prompt according to the question type or dynamic & then call openai API"
        # stage_4 = "Patch the data"
        # stage_5 = "Write the modified XML back to output file"

        try:
            target_page_id = "2010546873082608811"
            tree = ET.parse('output.xml')
            root = tree.getroot()
            # Namespace handling (if required)
            namespace = {'ns': 'http://lrncontent.lrn.com/schema/lcec/lrncourse'}
            ET.register_namespace('', namespace['ns'])  # Register default namespace
            # Find the <page> tag with the specific pageid
            page = root.find(f".//ns:page[@pageid='{target_page_id}']", namespace)
            question_element = page.find(".//ns:question", namespace)
            if question_element is not None and 'type' in question_element.attrib:
                question_type = question_element.attrib['type']
                print(f"Question type for page_id {target_page_id} is:", question_type)
                print("**********************************************")
                #now let's count number of <choices>/options for that question
                options_count = len(question_element.findall('.//ns:choice',namespace))
                print("options count for the question is:", options_count)
                print("**********************************************")
                #ternary to dynamically call the function based on the question type
                response = self.MCQ_Content_Generator(options_count, question_type)
                print(response)
                if response is not None:
                    self.xml_manipulator(response)


        except Exception as e:
            raise Exception(f"Error in MCQ_SAQ_Generator's main function: {str(e)}")    