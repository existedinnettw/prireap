import orjson
from fastapi.responses import JSONResponse, Response
from .. import schemas, crud, models
from typing import List, Optional, Any



class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes: #
        return orjson.dumps(content, default=str) #default=decimal_default)

class JSONDataResponse(JSONResponse): 
    #function override
    def render(self, content: str) -> bytes:#return bytes type by function bytes or encode
        return content.encode("utf-8")