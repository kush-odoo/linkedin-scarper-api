from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

class ScrapeRequest(BaseModel):
    url: HttpUrl = Field(
        ..., 
        example="https://www.linkedin.com/in/williamhgates",
        description="Public LinkedIn profile URL"
    )

class DateRange(BaseModel):
    starts_at: Optional[str] = Field(default=None, example="2020-01-01")
    ends_at: Optional[str] = Field(default=None, example="2023-05-31")

class Experience(BaseModel):
    title: Optional[str] = Field(default=None, example="Co-chair")
    company_name: Optional[str] = Field(default=None, example="Bill & Melinda Gates Foundation")
    location: Optional[str] = Field(default=None, example="Seattle, WA")
    description: Optional[str] = Field(default=None, example="Leading global health initiatives.")
    date_range: DateRange

class Education(BaseModel):
    school_name: Optional[str] = Field(default=None, example="Harvard University")
    degree_name: Optional[str] = Field(default=None, example="Bachelor of Science")
    field_of_study: Optional[str] = Field(default=None, example="Computer Science")
    date_range: DateRange

class Certification(BaseModel):
    name: Optional[str] = Field(default=None, example="AWS Certified Solutions Architect")
    authority: Optional[str] = Field(default=None, example="Amazon Web Services")
    license_number: Optional[str] = Field(default=None, example="12345678")
    url: Optional[str] = Field(default=None, example="https://aws.amazon.com/verify")

class Language(BaseModel):
    name: Optional[str] = Field(default=None, example="English")
    proficiency: Optional[str] = Field(default=None, example="NATIVE_OR_BILINGUAL")

class ProfileResponse(BaseModel):
    public_identifier: str = Field(..., example="williamhgates")
    first_name: Optional[str] = Field(default=None, example="Bill")
    last_name: Optional[str] = Field(default=None, example="Gates")
    headline: Optional[str] = Field(default=None, example="Co-chair, Bill & Melinda Gates Foundation")
    location: Optional[str] = Field(default=None, example="Seattle, Washington")
    about: Optional[str] = Field(default=None, example="Co-chair of the Bill & Melinda Gates Foundation...")
    profile_picture_url: Optional[str] = Field(default=None, example="https://media.licdn.com/dms/image/...")
    experiences: List[Experience] = []
    educations: List[Education] = []
    skills: List[str] = []
    certifications: List[Certification] = []
    languages: List[Language] = []
