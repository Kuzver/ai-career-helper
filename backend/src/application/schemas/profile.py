from pydantic import BaseModel


class ProfileResponse(BaseModel):
    name: str | None = None
    specialization: str | None = None
    experience_level: str | None = None
    skills: str | None = None
    career_goal: str | None = None


class ProfileUpdateRequest(BaseModel):
    name: str | None = None
    specialization: str | None = None
    experience_level: str | None = None
    skills: str | None = None
    career_goal: str | None = None
