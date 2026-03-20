import os
import json
import re
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv
from app.models import AnalyzeResponse, RoadmapItem
from app.courses import enrich_roadmap_with_serpapi
from app.jobs import fetch_relevant_jobs_for_role

env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_skills_map() -> dict:
    with open(DATA_DIR / "skills_map.json") as f:
        return json.load(f)


def _extract_skills_from_resume(resume_text: str, all_known_skills: list[str]) -> list[str]:
    text_lower = resume_text.lower()
    return [skill for skill in all_known_skills if skill.lower() in text_lower]


def _aggregate_required_skills(job_descriptions: list[dict]) -> list[str]:
    seen = set()
    skills = []
    for jd in job_descriptions:
        for skill in jd.get("required_skills", []):
            if skill not in seen:
                seen.add(skill)
                skills.append(skill)
    return skills


SYSTEM_PROMPT = """You are a precise career gap analysis engine. 
You receive a resume and target job descriptions, then output structured JSON only.
No preamble. No markdown fences. Raw JSON exactly matching the schema provided."""


def _build_user_prompt(resume_text: str, target_role: str, job_descriptions: list[dict]) -> str:
    jd_summary = json.dumps(
        [
            {
                "title": jd["title"],
                "required_skills": jd["required_skills"],
                "nice_to_have": jd.get("nice_to_have", []),
            }
            for jd in job_descriptions
        ],
        indent=2,
    )

    return f"""
You are a precise career gap analysis engine.

You receive:
- A target role title
- A candidate resume
- One or more job descriptions (with required and nice_to_have skills)

Your task:
- Compare the resume against the job descriptions for the target role.
- Identify which skills required by the jobs are clearly present in the resume and which are missing.
- Build a short, prioritised learning roadmap only for the missing skills.

Important principles:
- Treat any skill mentioned anywhere in the resume (skills section, experience bullets, projects, certifications, etc.) as PRESENT.
- A "skill" here is a concrete technology, tool, framework, language, or concept (e.g. Python, SQL, Docker, System Design).
- Be conservative: if it is unclear whether the candidate knows a skill, treat it as MISSING.

You must return ONLY a single JSON object with EXACTLY these keys and types:

{{
  "missing_skills": [
    "Skill name 1",
    "Skill name 2"
  ],
  "transferable_skills": [
    "Skill name already in resume that is relevant to the target role"
  ],
  "roadmap": [
    {{
      "skill": "Skill name that is currently missing",
      "why": "One short sentence about why this skill matters for the target role",
      "free_resource": "One specific free resource (e.g. official docs or a specific course/book)",
      "paid_resource": "One specific paid resource (e.g. a named course or book)",
      "estimated_weeks": 2
    }}
  ],
  "summary": "2-3 sentence plain English summary of the candidate's readiness and top learning priorities"
}}

Strict JSON rules:
- Do NOT include any additional keys or fields.
- Do NOT rename any keys.
- Do NOT wrap the JSON in markdown or backticks.
- Values must be valid JSON (no comments, no trailing commas).

Roadmap rules:
- Only include skills that appear in missing_skills.
- At most 6 roadmap items.
- Order roadmap items by impact/priority for the target role (most important first).
- estimated_weeks must be an integer between 1 and 8.
- Resource names must be specific and realistic (avoid generic text like "online course" or "read about X").

Now analyse the following data.

TARGET ROLE:
{target_role}

RESUME:
{resume_text}

JOB DESCRIPTIONS (JSON):
{jd_summary}
""".strip()


def _call_gemini(resume_text: str, target_role: str, job_descriptions: list[dict]) -> AnalyzeResponse | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            _build_user_prompt(resume_text, target_role, job_descriptions),
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4096,
            ),
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        )

        raw = response.text.strip()

        raw = re.sub(r"^```(?:json)?\s*\n?", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE)
        raw = raw.strip()

        data = json.loads(raw)

        roadmap = [RoadmapItem(**item) for item in data.get("roadmap", [])]

        roadmap = enrich_roadmap_with_serpapi(roadmap)

        return AnalyzeResponse(
            target_role=target_role,
            missing_skills=data.get("missing_skills", []),
            transferable_skills=data.get("transferable_skills", []),
            roadmap=roadmap,
            summary=data.get("summary", ""),
            ai_powered=True,
        )

    except Exception as e:
        print(f"[Gemini API error] {e}")
        return None


def _build_mock_questions_prompt(target_role: str, skills: list[str] | None = None) -> str:
    skills_part = ", ".join(skills) if skills else ""
    return f"""
You are an experienced technical interviewer.

Generate a focused list of 8 to 10 interview questions for a candidate interviewing for the role "{target_role}".
If a list of skills is provided, bias the questions towards those skills while still covering core fundamentals for the role.

Return ONLY a single JSON object of the form:
{{
  "questions": [
    "Question 1?",
    "Question 2?"
  ]
}}

Rules:
- Do not include any explanations, answers, or commentary, only the questions.
- Questions should be specific and realistic for real interviews.
- Mix conceptual questions with a few practical or scenario-based questions.
- Do not wrap the JSON in markdown or backticks.

TARGET ROLE:
{target_role}

FOCUS_SKILLS:
{skills_part}
""".strip()


def generate_mock_questions(target_role: str, skills: list[str] | None = None) -> list[str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return []

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = _build_mock_questions_prompt(target_role, skills)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1024,
            ),
        )
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*\n?", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE)
        raw = raw.strip()
        data = json.loads(raw)
        questions = data.get("questions")
        if isinstance(questions, list):
            return [q for q in questions if isinstance(q, str) and q.strip()]
        return []
    except Exception as e:
        print(f"[Gemini mock questions error] {e}")
        return []


def _rule_based_fallback(
    resume_text: str,
    target_role: str,
    job_descriptions: list[dict],
) -> AnalyzeResponse:
    skills_map = _load_skills_map()

    all_known_skills = [
        skill
        for category_skills in skills_map["categories"].values()
        for skill in category_skills
    ]
    resources = skills_map.get("learning_resources", {})

    resume_skills = set(_extract_skills_from_resume(resume_text, all_known_skills))
    required_skills = _aggregate_required_skills(job_descriptions)

    missing = [s for s in required_skills if s not in resume_skills]
    transferable = [s for s in resume_skills if s in required_skills or s in all_known_skills]

    roadmap = []
    for skill in missing[:6]:
        res = resources.get(
            skill,
            {
                "free": f"Search '{skill} tutorial' on YouTube or official docs",
                "paid": f"Search '{skill}' on Udemy or Coursera",
            },
        )

        roadmap.append(
            RoadmapItem(
                skill=skill,
                why=f"{skill} is listed as a required skill for {target_role} roles.",
                free_resource=res.get("free", "Official documentation"),
                paid_resource=res.get("paid", "Udemy / Coursera"),
                estimated_weeks=2,
            )
        )

    roadmap = enrich_roadmap_with_serpapi(roadmap)

    n_missing = len(missing)
    n_transfer = len(transferable)
    summary = (
        f"You have {n_transfer} transferable skill(s) relevant to {target_role}. "
        f"There are {n_missing} skill gap(s) identified based on typical job requirements. "
        f"Focus on the top items in the roadmap to become competitive quickly. "
        f"(Note: this analysis used the rule-based fallback — add a GEMINI_API_KEY for AI-powered insights.)"
    )

    return AnalyzeResponse(
        target_role=target_role,
        missing_skills=missing,
        transferable_skills=transferable,
        roadmap=roadmap,
        summary=summary,
        ai_powered=False,
    )


def analyze_gap(
    resume_text: str,
    target_role: str,
    job_descriptions: list[dict],
    experience_level: str | None = None,
) -> AnalyzeResponse:
    result = _call_gemini(resume_text, target_role, job_descriptions)
    if result is None:
        result = _rule_based_fallback(resume_text, target_role, job_descriptions)

    suggested = fetch_relevant_jobs_for_role(target_role, experience_level)
    if suggested:
        result.suggested_jobs = suggested

    return result
