from pydantic import BaseModel

class InputText(BaseModel):
    text : str
    context : str
    rules  : str
    task : str

class Response(BaseModel):
    response:str