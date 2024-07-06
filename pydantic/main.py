import json
import pprint
from typing import List, Optional
from pydantic import BaseModel, field_validator


class Type(BaseModel):
    breed: str
    age: float
    name: str
    temperament: str


class Dog(BaseModel):
    id: int
    title: str
    types: Optional[List[Type]]
    
    @field_validator('id')
    def id_validator(cls, value) -> int:
        if len(str(value)) != 3:
            raise ValueError('ID has to be 3 chars')
        return value


# my_dog: Dog = Dog(id=12345,
#     title="Dogs",
#     types=[
#         Type(
#             name="Buffy",
#             breed="Cane Corso",
#             age=6,
#             temperament="Mad"
#         )
#     ])

# print(my_dog.types[0].name)

with open("/Users/john/work/github/Python/pydantic/data.json") as f:
    data: dict = json.load(f)
    dogs: list = [Dog(**dog) for dog in data['info']]
    
    pprint.pprint(dogs)