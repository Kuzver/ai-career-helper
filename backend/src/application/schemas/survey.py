from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class SurveyOptionOut(BaseModel):
    id: UUID
    text: str
    order: int


class SurveyQuestionOut(BaseModel):
    id: UUID
    text: str
    question_type: str
    is_required: bool = True
    order: int
    options: list[SurveyOptionOut]


class SurveyListItem(BaseModel):
    id: UUID
    title: str
    description: str | None
    is_mandatory: bool
    is_completed: bool = False


class SurveyDetail(BaseModel):
    id: UUID
    title: str
    description: str | None
    is_mandatory: bool
    questions: list[SurveyQuestionOut]


class AnswerSubmit(BaseModel):
    question_id: UUID
    option_id: UUID | None = None
    free_text: str | None = None


class SurveySubmitRequest(BaseModel):
    answers: list[AnswerSubmit]


class SurveySubmitResponse(BaseModel):
    response_id: UUID
    is_validated: bool
    validation_result: str | None


# Admin schemas

class SurveyOptionCreate(BaseModel):
    text: str
    order: int = 0


class SurveyQuestionCreate(BaseModel):
    text: str
    question_type: str = "single"
    is_required: bool = True
    order: int = 0
    options: list[SurveyOptionCreate] = []


class SurveyCreate(BaseModel):
    title: str
    description: str | None = None
    is_mandatory: bool = False
    questions: list[SurveyQuestionCreate] = []


class SurveyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_mandatory: bool | None = None
    is_active: bool | None = None
    questions: list[SurveyQuestionCreate] | None = None
