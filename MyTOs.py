""" 
Description: 
 - Data transfer object

History:
 - 2024/05/21 by Hysun (hysun.he@oracle.com): Initial version
"""

import pydantic
from pydantic import BaseModel


class Response(BaseModel):
    """DTO class"""

    status: str = pydantic.Field(..., description="status text")
    message: str = pydantic.Field(..., description="message text")
    data: dict = pydantic.Field(..., description="response data")


class QueryPara(BaseModel):
    text: str = pydantic.Field(..., description="query text")
