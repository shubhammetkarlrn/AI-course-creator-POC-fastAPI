from typing import List, Dict, Any
from .MCQ_Template_QuickQuiz import MCQ_Template
from .clickAndReveal import ClickAndReveal_Template
from .TextAndImage import TextAndImage_Template
from .MCQ_SAQ import MCQ_SAQ_Template
from .videoSlideShow import videoSlideShow_Template
import xml.etree.ElementTree as ET

class DataMapper:
    async def map_and_modify(self, llm_response: Any) :
        mcq_template_flow = MCQ_Template()
        click_and_reveal_template_flow = ClickAndReveal_Template()
        text_and_image_template_flow = TextAndImage_Template()
        mcq_saq_template_flow = MCQ_SAQ_Template()
        video_slide_show_template_flow = videoSlideShow_Template()
        
        try:
            print("------------------ starting videoSlideShow Template ------------------")
            await video_slide_show_template_flow.videoSlideShowGenerator(llm_response)

            print("------------------ starting MCQ Lesson QuickQuiz Template ------------------")
            await mcq_template_flow.MCQ_generator()

            print("------------------ starting click and reveal Template ------------------")
            await click_and_reveal_template_flow.clickAndRevealGenerator()

            print("------------------ starting Text and Image Template ------------------")
            await text_and_image_template_flow.textAndImageGenerator()

            print("------------------ starting MCQ-SAQ Template ------------------")
            await mcq_saq_template_flow.MCQ_SAQ_Generator()

            
            return ""  # Replace with actual modified XML
        except Exception as e:
            raise Exception(f"Error in data mapping: {str(e)}")