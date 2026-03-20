from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
from pathlib import Path
from dotenv import load_dotenv

env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)

from app.analyzer import analyze_gap
from app.models import AnalyzeRequest, AnalyzeResponse, JobDescription

app = FastAPI(
    title="SkillBridge Career Navigator API",
    description="AI-powered skill gap analysis and learning roadmap generator",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent.parent / "data"


@app.get("/")
def root():
    return {"message": "SkillBridge API is running", "docs": "/docs"}


@app.get("/roles", response_model=list[str])
def get_available_roles():
    with open(DATA_DIR / "job_descriptions.json") as f:
        jds = json.load(f)
    return sorted(set(jd["title"] for jd in jds))


@app.get("/jobs", response_model=list[JobDescription])
def get_job_descriptions(role: Optional[str] = None):
    with open(DATA_DIR / "job_descriptions.json") as f:
        jds = json.load(f)
    if role:
        jds = [jd for jd in jds if role.lower() in jd["title"].lower()]
    return jds


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    if not request.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")
    if not request.target_role.strip():
        raise HTTPException(status_code=400, detail="Target role cannot be empty.")

    with open(DATA_DIR / "job_descriptions.json") as f:
        all_jds = json.load(f)

    matching_jds = [
        jd for jd in all_jds if request.target_role.lower() in jd["title"].lower()
    ] or all_jds

    result = analyze_gap(
        resume_text=request.resume_text,
        target_role=request.target_role,
        job_descriptions=matching_jds,
        experience_level=request.experience_level,
    )
    return result


@app.get("/sample-resumes")
def get_sample_resumes():
    with open(DATA_DIR / "sample_resumes.json") as f:
        return json.load(f)
