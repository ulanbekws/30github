from typing import Annotated
from annotated_types import MaxLen, MinLen

from pydantic import BaseModel


class CreateUser(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(20)]
    email: str