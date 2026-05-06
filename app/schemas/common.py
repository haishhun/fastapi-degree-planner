from pydantic import BaseModel


class ResponseMessage(BaseModel):
    detail: str
