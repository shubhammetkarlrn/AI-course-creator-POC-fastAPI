from openai import OpenAI
from app.core.config import get_settings
import json
import xml.etree.ElementTree as ET
import time

class MCQ_Template:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY) 

    def adaptive_section_creator(self, course_outline_dict):
        all_sections = ""
        for index, qna_pair in enumerate(course_outline_dict['qna_pairs']):
            pageid = f"adapt_001_{index+2}"
            qId = str(index+1)
            interactionId = f"QQ-lesson_1179347450018272246-{qId}"
            question_text = qna_pair['question']
            answer = qna_pair['answer'].strip().lower()  # Normalize the answer for comparison
             # Determine the correct choice based on the answer
            if answer == "true":
                true_is_correct = "true"
                false_is_correct = "false"
            else:
                true_is_correct = "false"
                false_is_correct = "true"
            
            section = f"""
            <question lessonId="lesson_1179347450018272246" pageid="{pageid}" qId="{qId}" interactionId="{interactionId}" type="multipleChoice">
                <title/>
                <questionText>
                    <adpQuestionText>
                        <adpAssessmentQuestion>
                            <p>{question_text}</p>
                        </adpAssessmentQuestion>
                    </adpQuestionText>
                </questionText>
                <choice isCorrect="{true_is_correct}">
                    <adpQuestionAnswer>
                        <adpAssessmentAnswer_0>
                            <p>True</p>
                        </adpAssessmentAnswer_0>
                    </adpQuestionAnswer>
                </choice>
                <choice isCorrect="{false_is_correct}">
                    <adpQuestionAnswer>
                        <adpAssessmentAnswer_1>
                            <p>False</p>
                        </adpAssessmentAnswer_1>
                    </adpQuestionAnswer>
                </choice>
                <feedback/>
            </question>
            """
            all_sections += section
            before_content = f"""
            <adaptive passingCount="4" randomize="true" poolSize="5">
                <landing lessonId="lesson_1179347450018272246" pageid="adapt_001_1">
                    <title>Ready to show what you know?</title>
                    <text>
                        <adpLandingPageContent/>
                    </text>
                </landing>\n        
            """
            after_content = f"""
            \n<result lessonId="lesson_1179347450018272246" pageid="adapt_001_12">
                <feedback feedbackId="correct">
                    <title> </title>
                    <text>
                        <adpPassMessageText>
                            <p>You've got it!</p>
                        </adpPassMessageText>
                    </text>
                </feedback>
                <feedback feedbackId="incorrect">
                    <title> </title>
                    <text>          
                        <adpFailMessageText>
                            <p>Sorry, you'll need to retake the assessment.</p>
                        </adpFailMessageText>
                    </text>
                </feedback>
              </result>           
              <wrapUp lessonId="lesson_1179347450018272246" pageid="adapt_001_13">
                <title/>
                <text>
                    <adpWrapUpPageContent/>
                </text>
              </wrapUp>      
            </adaptive>
            """
            final_adaptive_xml = before_content + all_sections + after_content
        # print(all_sections)
        return final_adaptive_xml


    def xml_manipulation(self, final_adaptive_xml):
        try:
            tree = ET.parse('output.xml')
            # print(ET.tostring(tree.getroot(), encoding='utf8').decode('utf8'))
            root = tree.getroot()
            # Namespace handling (if required)
            namespace = {'ns': 'http://lrncontent.lrn.com/schema/lcec/lrncourse'}
            ET.register_namespace('', namespace['ns'])  # Register default namespace
            if(root is None):
                print("No root found")
                return
            first_topic = root.find('.//ns:topic',namespace)
            if(first_topic is None):
                print("No first_topic found")
                return
            for section in root.findall('.//ns:topic',namespace):
                print(ET.tostring(section, encoding='utf8').decode('utf8'))
                print("**********************************************")
                adaptive_element = section.find('.//ns:adaptive',namespace)
                if adaptive_element is not None:
                    print("adaptive_element found")
                    print("adaptive_element", adaptive_element)
                    print("**********************************************")
                    print("final_adaptive_xml", final_adaptive_xml)
                    print(type(final_adaptive_xml))
                    # Find the index of the existing `<adaptive>` element to remove it
                    adaptive_index = list(section).index(adaptive_element)
                    section.remove(adaptive_element)
                    new_section_element = ET.fromstring(final_adaptive_xml)
                    section.insert(adaptive_index, new_section_element)
                    break
            tree.write('output.xml', encoding='utf-8', xml_declaration=True)
        except Exception as e:
            raise Exception(f"Error in manipulating XML: {str(e)}")     


    async def MCQ_generator(self):
        try:
            mcq_format_function = {
                "name": "generate_mcq_template",
                "description": "Generates MCQ set on the specified topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "qna_pairs": {
                            "type": "array",
                            "description": "A list of QnA pairs",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {
                                        "type": "string",
                                        "description": "The question description"
                                    },
                                    "answer": {
                                        "type": "string",
                                        "description": "Answer for the question in True/False format"
                                    }
                                },
                                "required": ["question", "answer"]
                            }
                        }
                    },
                    "required": ["qna_pairs"]
                }
            }

            # Add your OpenAI API call logic here
            prompt = f"Generate 10 sets of multiple-choice questions (MCQs) for a course on ethics in the workplace in hospitality industry. A question could be either factual questions or scenario/situational questions. Every question is either true or false, with only one correct answer. Here are some examples for the reference: \n Factual Question example: Harassment is unwelcome conduct, specifically of a physical or sexual nature, that leaves the victim physically or emotionally damaged. It does not apply to verbal and/or visual conduct. \n Scenario/Situational Question example: Youssef wears religious headgear. Sandra teases him about how “stupid it looks.” Could this be considered harassment? ."
            system_prompt = "You are a Course Creation Agent at a popular online learning platform. Your role is to assist customers who are interested in creating courses on the platform. You have extensive knowledge of the course creation process and are familiar with the platform's guidelines and requirements. Your goal is to provide helpful and accurate information to customers, addressing their inquiries and guiding them through the course creation process. You are now tasked with generating multiple-choice questions (MCQs) for a course on ethics in the workplace in hospitality industry."

            # Log the start time
            start_time = time.time()

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                functions=[mcq_format_function],  # Add the function definition
                function_call={"name": "generate_mcq_template"}  # Force calling the function
            )

            # Log the end time
            end_time = time.time()
            # Calculate the time taken
            time_taken = end_time - start_time
            print(f"Time taken for OpenAI LLM call for MCQs generation: {time_taken} seconds")
                        
            course_outline_dict = json.loads(response.choices[0].message.function_call.arguments) #this is a dictionary
            final_adaptive_xml = self.adaptive_section_creator(course_outline_dict)
            #here we'll call one more function which will take this final_adaptive_xml & patch into the source XML
            self.xml_manipulation(final_adaptive_xml)
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")       
        