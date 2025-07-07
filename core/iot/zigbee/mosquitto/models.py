from pydantic import BaseModel

class AddUserRequest(BaseModel):
    username: str
    password: str

class RemoveUserRequest(BaseModel):
    username: str

class UserResponse(BaseModel):
    username: str
    status: str