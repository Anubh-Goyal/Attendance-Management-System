from pydantic import BaseModel


class AdminConfigRequest(BaseModel):
    domain_name: str
    sub_domain_name: str
