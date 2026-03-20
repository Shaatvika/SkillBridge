import os
from serpapi import GoogleSearch
from app.models import SuggestedJob


def _title_matches_experience(title: str, experience_level: str | None) -> bool:
    if not experience_level or not title:
        return True

    t = title.lower()
    senior_markers = ["senior", "sr.", "lead", "principal", "staff", "manager", "head"]

    if experience_level.lower() == "junior":
        return not any(m in t for m in senior_markers)

    if experience_level.lower() == "senior":
        return True

    return True


def fetch_relevant_jobs_for_role(role: str, experience_level: str | None = None) -> list[SuggestedJob]:
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return []

    level_hint = ""
    if experience_level:
        m = {
            "junior": "junior OR entry level OR associate",
            "mid": "mid level OR intermediate",
            "senior": "senior OR lead OR principal",
        }
        level_hint = m.get(experience_level.lower(), experience_level)

    q = role
    if level_hint:
        q = f"{role} ({level_hint})"

    try:
        params = {
            "engine": "google_jobs",
            "q": q,
            "hl": "en",
            "api_key": api_key,
        }
        search = GoogleSearch(params)
        results = search.get_dict() or {}
        jobs = results.get("jobs_results", [])

        suggested: list[SuggestedJob] = []
        for job in jobs:
            title = job.get("title") or ""
            if not _title_matches_experience(title, experience_level):
                continue

            company = job.get("company_name") or ""
            location = job.get("location")

            apply_opts = job.get("apply_options") or []
            link = apply_opts[0].get("link") if apply_opts and isinstance(apply_opts[0], dict) else None

            desc = job.get("description") or ""
            snippet = (desc[:220] + "...") if desc else None

            suggested.append(
                SuggestedJob(
                    title=title,
                    company=company,
                    location=location,
                    link=link,
                    snippet=snippet,
                )
            )

            if len(suggested) >= 5:
                break

        return suggested
    except Exception:
        return []
