from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., description="Raw resume text pasted by the user")
    target_role: str = Field(..., description="Job title the user is targeting")
    experience_level: Optional[str] = Field(
        default=None,
        description="User-selected experience level (e.g. junior, mid, senior)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_text": "BS Computer Science. Skills: Python, SQL, Git. Interned at LocalStartup building REST APIs.",
                "target_role": "Machine Learning Engineer",
                "experience_level": "junior",
            }
        }
    }


class RoadmapItem(BaseModel):
    skill: str
    why: str = Field(..., description="Why this skill matters for the role")
    free_resource: str
    paid_resource: str
    estimated_weeks: int
    certifications: Optional[list[str]] = Field(
        default=None,
        description="Optional list of recommended certifications for this skill",
    )


class SuggestedJob(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    link: Optional[str] = None
    snippet: Optional[str] = None


class AnalyzeResponse(BaseModel):
    target_role: str
    missing_skills: list[str] = Field(..., description="Skills required but not found in resume")
    transferable_skills: list[str] = Field(..., description="Skills from resume that are relevant")
    roadmap: list[RoadmapItem] = Field(..., description="Ordered learning path")
    summary: str = Field(..., description="One-paragraph plain-English summary")
    ai_powered: bool = Field(..., description="True if Claude API was used; False if fallback was used")
    suggested_jobs: Optional[list[SuggestedJob]] = Field(
        default=None,
        description="Relevant live job postings based on the target role",
    )


class JobDescription(BaseModel):
    id: str
    title: str
    company: str
    required_skills: list[str]
    nice_to_have: list[str]
    description: str
