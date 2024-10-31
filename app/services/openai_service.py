from openai import OpenAI
from app.core.config import get_settings
from typing import List, Dict, Any
import json
import xml.etree.ElementTree as ET

class OpenAIService:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY)
    
    def get_completion(self, data: Any, request: Any):
        """
        Get completion from OpenAI based on the provided data
        """
        try:
            # Define the function schema (what data you expect from the API)
            course_outline_function = {
                "name": "generate_course_outline",
                "description": "Generates a course outline on the specified topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "chapters": {
                            "type": "array",
                            "description": "A list of course chapters",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "chapter_number": {
                                        "type": "integer",
                                        "description": "The chapter number"
                                    },
                                    "title": {
                                        "type": "string",
                                        "description": "The title of the chapter"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "The description of the chapter"
                                    }
                                },
                                "required": ["chapter_number", "title", "description"]
                            }
                        }
                    },
                    "required": ["chapters"]
                }
            }


            # Add your OpenAI API call logic here
            prompt = f"create a course outline for ethics course for {request.course_topic_area} in the workplace for industry {request.industry}, including chapter titles and descriptions for each chapter.\n\nBe slightly verbose, highly creative."
            system_prompt = "You are a Course Creation Agent at a popular online learning platform. Your role is to assist customers who are interested in creating courses on the platform. You have extensive knowledge of the course creation process and are familiar with the platform's guidelines and requirements. Your goal is to provide helpful and accurate information to customers, addressing their inquiries and guiding them through the course creation process."

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                functions=[course_outline_function],  # Add the function definition
                function_call={"name": "generate_course_outline"}  # Force calling the function
            )
                        
            course_outline_dict = json.loads(response.choices[0].message.function_call.arguments) #this is a dictionary
            print("**********************************************")
            print("Entire course outline dict is", course_outline_dict)
            first_chapter = course_outline_dict['chapters'][0]
            first_chapter_title = first_chapter['title']
            first_chapter_description = first_chapter['description']
            print("**********************************************")
            root = ET.fromstring(data)
            # Find and replace the <title> text inside <page>
            # Find and replace the first <title> tag inside <page>
            page_title = root.find(".//page/title")
            if page_title is not None:
                page_title.text = first_chapter_title

            # Find and replace the <p> tag inside the first <text> under <page>
            page_text_p = root.find(".//page/text/p")
            if page_text_p is not None:
                page_text_p.text = first_chapter_description

            # Output the modified XML
            new_xml = ET.tostring(root, encoding='unicode')
            print(new_xml)
            print("**********************************************")
            print(type(response.choices[0].message.function_call.arguments))
            values = [first_chapter_title, first_chapter_description]
            return values #returning the modified xml for first lesson
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")

