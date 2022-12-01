from pydantic import BaseModel

class VisibilityData(BaseModel):
    public: bool