from fastapi import APIRouter, HTTPException
from app.models.schemas import ProcessRequestBody, ProcessResponse
from app.services.xml_service import XMLProcessor
from app.services.openai_service import OpenAIService
from app.services.mapping_service import DataMapper
from app.services.external_api_service import ExternalAPIService

router = APIRouter()

@router.post("/process", response_model=ProcessResponse)
async def process_data(request: ProcessRequestBody):
    try:
        # Initialize services
        xml_processor = XMLProcessor()
        openai_service = OpenAIService()
        data_mapper = DataMapper()
        external_api = ExternalAPIService()

        # Step 1: Process XML
        xml_data = xml_processor.extract_data()
        
        # Step 2: Get OpenAI response
        llm_response = openai_service.get_completion(xml_data, request)
        
        # Step 3: Map data and modify XML
        modified_xml = data_mapper.map_and_modify(llm_response)
        
        # Step 4: Send to external API
        result = await external_api.send_xml(modified_xml)
        
        return ProcessResponse(
            status="success",
            message="Processing completed successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
