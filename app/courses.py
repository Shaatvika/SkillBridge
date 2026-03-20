import os
from serpapi import GoogleSearch
from app.models import RoadmapItem


CERT_FALLBACK: dict[str, list[str]] = {
    "AWS": ["AWS Certified Solutions Architect – Associate"],
    "Docker": ["Docker Certified Associate"],
    "Kubernetes": ["Certified Kubernetes Administrator (CKA)"],
    "Security": ["CompTIA Security+"],
    "Network Security": ["CompTIA Security+"],
    "SIEM": ["GIAC Certified Incident Handler (GCIH)"],
    "Incident Response": ["GIAC Certified Incident Handler (GCIH)"],
    "Data Engineer": ["Google Professional Data Engineer"],
}


def _fetch_certifications_for_skill(skill: str, api_key: str) -> list[str] | None:
    try:
        params = {
            "engine": "google",
            "q": f"{skill} certification",
            "api_key": api_key,
        }
        search = GoogleSearch(params)
        results = search.get_dict() or {}
        organic_results = results.get("organic_results", [])
        if not organic_results:
            return None

        certs: list[str] = []
        for result in organic_results[:3]:
            title = (result.get("title") or "").strip()
            if not title:
                continue
            if "certification" in title.lower() or "certified" in title.lower():
                certs.append(title)
        seen = set()
        deduped: list[str] = []
        for c in certs:
            if c not in seen:
                seen.add(c)
                deduped.append(c)
        return deduped[:2] if deduped else None
    except Exception:
        return None


def enrich_roadmap_with_serpapi(roadmap: list[RoadmapItem]) -> list[RoadmapItem]:
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        enriched = []
        for item in roadmap:
            certs = CERT_FALLBACK.get(item.skill)
            enriched.append(
                RoadmapItem(
                    skill=item.skill,
                    why=item.why,
                    free_resource=item.free_resource,
                    paid_resource=item.paid_resource,
                    estimated_weeks=item.estimated_weeks,
                    certifications=certs,
                )
            )
        return enriched

    enriched: list[RoadmapItem] = []
    enriched_count = 0
    for item in roadmap:
        try:
            params = {
                "engine": "google",
                "q": f"{item.skill} coursera course",
                "api_key": api_key,
            }
            search = GoogleSearch(params)
            results = search.get_dict() or {}
            organic_results = results.get("organic_results", [])

            free_resource = item.free_resource
            paid_resource = item.paid_resource

            if organic_results:
                first = organic_results[0]
                free_resource = f"{first.get('title', 'Course')} - {first.get('link', '')}".strip()
                if len(organic_results) > 1:
                    second = organic_results[1]
                    paid_resource = f"{second.get('title', 'Course')} - {second.get('link', '')}".strip()
                enriched_count += 1

            certs = _fetch_certifications_for_skill(item.skill, api_key)
            if not certs:
                certs = CERT_FALLBACK.get(item.skill)

            enriched.append(
                RoadmapItem(
                    skill=item.skill,
                    why=item.why,
                    free_resource=free_resource,
                    paid_resource=paid_resource,
                    estimated_weeks=item.estimated_weeks,
                    certifications=certs,
                )
            )
        except Exception:
            print("[SerpAPI] enrichment skipped")
            certs = CERT_FALLBACK.get(item.skill)
            enriched.append(
                RoadmapItem(
                    skill=item.skill,
                    why=item.why,
                    free_resource=item.free_resource,
                    paid_resource=item.paid_resource,
                    estimated_weeks=item.estimated_weeks,
                    certifications=certs,
                )
            )

    if enriched_count:
        print(f"[SerpAPI] enriched {enriched_count} roadmap item(s)")

    return enriched
