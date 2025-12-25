from fastapi.responses import JSONResponse


class OkResponse(JSONResponse):
    def __init__(self, message: str):
        super().__init__(status_code=200, content={"detail": message})
