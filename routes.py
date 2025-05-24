from fastapi import APIRouter, HTTPException, status
from PromptBuilder import PromptBuilder
from models import InputText, Response
from llm import LLM

router = APIRouter()

llm = LLM()
prompt_builder = PromptBuilder()

@router.post("/generate", response_model=Response, status_code=status.HTTP_200_OK)
async def generate(data: InputText):
    print("[API] /generate called")
    try:
        prompt = prompt_builder.build_prompt(
            template_name="exemple",
            input_object=data,
            output_class=Response
        )
        response = llm.generate(
            prompt=prompt,
            class_output=Response
        )
        print(response)
        return response

    except Exception as e:
        print(f"[API][ERROR] generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {e}"
        )
