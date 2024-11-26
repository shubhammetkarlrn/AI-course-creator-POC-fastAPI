import asyncio
from openai import OpenAI
from app.core.config import get_settings
import json
import xml.etree.ElementTree as ET
import time


class courseCreatorOutline:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY)

    async def courseOutline(self):
        try:
            course_topic_area = "Anti-bribery & Corruption"
            industry = "Banking"
            course_outline_function = {
                "name": "generate_course_outline",
                "description": "Generates a course outline with lessons and pages",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lessons": {
                            "type": "array",
                            "description": "A list of lessons in the course",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "lessonName": {
                                        "type": "string",
                                        "description": "The name of the lesson"
                                    },
                                    "pages": {
                                        "type": "array",
                                        "description": "A list of pages in the lesson",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "page_id": {
                                                    "type": "string",
                                                    "description": "The ID of the page"
                                                },
                                                "page_name": {
                                                    "type": "string",
                                                    "description": "The name of the page"
                                                },
                                                "content": {
                                                    "type": "string",
                                                    "description": "The content of the page"
                                                },
                                                "type": {
                                                    "type": "string",
                                                    "description": "The type of the page (e.g., videoSlideShow, textAndImage, ClickAndReveal, MCQ)"
                                                }
                                            },
                                            "required": ["page_id", "page_name", "content", "type"]
                                        }
                                    }
                                },
                                "required": ["lessonName", "pages"]
                            }
                        }
                    },
                    "required": ["lessons"]
                }
            }

            system_prompt = "You are a Course Creation Agent at a popular online learning platform. Your role is to assist customers who are interested in creating courses on the platform. You have extensive knowledge of the course creation process and are familiar with the platform's guidelines and requirements. Your goal is to provide helpful and accurate information to customers, addressing their inquiries and guiding them through the course creation process."

            user_prompt = f"""
            Generate a course outline for a course on {course_topic_area} in the {industry} industry. The course should have multiple lessons, each with several pages. Each page should have a unique ID, name, content, and type. The content should be engaging, informative, and relevant to the course topic area and industry.
            Use your own intelligence/creativity to provide below(focus will be only on text content generation part):
                - Number of lessons
                - Lesson titles
                - Brief lesson descriptions
            A lesson has multiple pages.
            Each page inside a lesson is a template like currently below are the templates used for the customisation of a course by our employees.
            Templates as below:
                - videoSlideShow (this template shows video & a related learning content on screen)
                - ClickAndReveal (this template has clickable box, on which clicked displays some content) 
                - TextAndImage (this template shows an image  & some related learning in text format) 
                - MCQ (this template creates a MCQ based on previous page's learning- MCQ could be only one answer correct or more than one answers correct)

            So I want you to use your intelligence to create the entire outline of the course, i.e use your own creativity/experience to decide how many lessons for the course, each lesson will have how many pages & each page will be of which template type(template types already mentioned above)
            """

            # Log the start time
            start_time = time.time()
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                functions=[course_outline_function],  # Add the function definition
                function_call={"name": "generate_course_outline"}  # Force calling the function
            )
            text_and_image_content = json.loads(response.choices[0].message.function_call.arguments)  # this is a dictionary
            print(text_and_image_content)
            # Log the end time
            end_time = time.time()
            # Calculate the time taken
            time_taken = end_time - start_time
            print(f"Time taken for OpenAI LLM call for Text&Image template content generation: {time_taken} seconds")

            with open('outline.json', 'w') as file:
                json.dump(text_and_image_content, file)
            return text_and_image_content
            
        except Exception as e:
            raise Exception(f"Error in Course Outline Generation: {str(e)}")        