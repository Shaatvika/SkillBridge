import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.analyzer import _rule_based_fallback, _extract_skills_from_resume

client = TestClient(app)


SAMPLE_RESUME = """
BS Computer Science, State University 2024.
Skills: Python, SQL, Git, HTML, CSS.
Intern at LocalStartup: built REST APIs in Python, wrote SQL queries.
Personal projects: CLI todo app, personal blog site.
"""

SAMPLE_JDS = [
    {
        "id": "jd_test_001",
        "title": "Machine Learning Engineer",
        "company": "TestCo",
        "required_skills": ["Python", "PyTorch", "scikit-learn", "SQL", "Statistics"],
        "nice_to_have": ["MLflow", "Docker"],
        "description": "Train and deploy ML models.",
    }
]


class TestAnalyzeEndpoint:
    def test_analyze_happy_path_fallback(self):
        with patch.dict("os.environ", {}, clear=True):
            response = client.post(
                "/analyze",
                json={
                    "resume_text": SAMPLE_RESUME,
                    "target_role": "Machine Learning Engineer",
                },
            )
        assert response.status_code == 200
        data = response.json()

        assert "missing_skills" in data
        assert "transferable_skills" in data
        assert "roadmap" in data
        assert "summary" in data
        assert "ai_powered" in data
        assert "target_role" in data

        assert isinstance(data["missing_skills"], list)
        assert isinstance(data["transferable_skills"], list)
        assert isinstance(data["roadmap"], list)
        assert isinstance(data["summary"], str)
        assert len(data["summary"]) > 0

        transferable_lower = [s.lower() for s in data["transferable_skills"]]
        assert "python" in transferable_lower or "sql" in transferable_lower

    def test_analyze_ai_powered_path(self):
        mock_response_text = """{
            "missing_skills": ["PyTorch", "scikit-learn", "Statistics"],
            "transferable_skills": ["Python", "SQL"],
            "roadmap": [
                {
                    "skill": "PyTorch",
                    "why": "Core framework for ML model training.",
                    "free_resource": "PyTorch official tutorials",
                    "paid_resource": "fast.ai deep learning course",
                    "estimated_weeks": 4
                }
            ],
            "summary": "You have a solid Python foundation. Focus on ML frameworks to become competitive."
        }"""

        mock_response = MagicMock()
        mock_response.text = mock_response_text

        with patch("app.analyzer.genai.GenerativeModel") as mock_model_cls:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_model_cls.return_value = mock_model

            with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
                response = client.post(
                    "/analyze",
                    json={
                        "resume_text": SAMPLE_RESUME,
                        "target_role": "Machine Learning Engineer",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["ai_powered"] is True
        assert "PyTorch" in data["missing_skills"]
        assert "Python" in data["transferable_skills"]
        assert len(data["roadmap"]) == 1
        assert data["roadmap"][0]["skill"] == "PyTorch"

    def test_roles_endpoint(self):
        response = client.get("/roles")
        assert response.status_code == 200
        roles = response.json()
        assert isinstance(roles, list)
        assert len(roles) > 0
        assert all(isinstance(r, str) for r in roles)

    def test_jobs_endpoint_all(self):
        response = client.get("/jobs")
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)
        assert len(jobs) > 0

    def test_jobs_endpoint_filtered(self):
        response = client.get("/jobs?role=Cloud Engineer")
        assert response.status_code == 200
        jobs = response.json()
        assert all("Cloud" in job["title"] or "Engineer" in job["title"] for job in jobs)

    def test_sample_resumes_endpoint(self):
        response = client.get("/sample-resumes")
        assert response.status_code == 200
        resumes = response.json()
        assert isinstance(resumes, list)
        assert len(resumes) > 0


class TestEdgeCases:
    def test_empty_resume_rejected(self):
        response = client.post(
            "/analyze",
            json={
                "resume_text": "   ",
                "target_role": "Software Engineer",
            },
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_empty_role_rejected(self):
        response = client.post(
            "/analyze",
            json={
                "resume_text": SAMPLE_RESUME,
                "target_role": "   ",
            },
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_unknown_role_falls_back_to_all_jds(self):
        with patch.dict("os.environ", {}, clear=True):
            response = client.post(
                "/analyze",
                json={
                    "resume_text": SAMPLE_RESUME,
                    "target_role": "Quantum Wizard",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert "roadmap" in data

    def test_resume_with_all_skills(self):
        expert_resume = """
        Skills: Python, PyTorch, scikit-learn, SQL, Statistics, MLflow, Docker,
        Kubernetes, AWS, Spark, Transformers, Data Preprocessing.
        10 years experience as ML Engineer.
        """
        result = _rule_based_fallback(
            resume_text=expert_resume,
            target_role="Machine Learning Engineer",
            job_descriptions=SAMPLE_JDS,
        )
        assert result.missing_skills == []
        assert len(result.transferable_skills) > 0

    def test_claude_api_failure_triggers_fallback(self):
        with patch("app.analyzer.genai.GenerativeModel") as mock_model_cls:
            mock_model_cls.side_effect = Exception("Connection timeout")
            with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
                response = client.post(
                    "/analyze",
                    json={
                        "resume_text": SAMPLE_RESUME,
                        "target_role": "Software Engineer",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["ai_powered"] is False
        assert "roadmap" in data

    def test_roadmap_capped_at_six_items(self):
        minimal_resume = "I know nothing. No skills whatsoever."
        result = _rule_based_fallback(
            resume_text=minimal_resume,
            target_role="Machine Learning Engineer",
            job_descriptions=SAMPLE_JDS,
        )
        assert len(result.roadmap) <= 6


class TestHelpers:
    def test_extract_skills_case_insensitive(self):
        resume = "I use python and SQL daily. Also familiar with git."
        skills = _extract_skills_from_resume(resume, ["Python", "SQL", "Git", "Docker"])
        assert "Python" in skills
        assert "SQL" in skills
        assert "Git" in skills
        assert "Docker" not in skills

    def test_extract_skills_empty_resume(self):
        skills = _extract_skills_from_resume("", ["Python", "SQL"])
        assert skills == []


class TestSerpapiAndExperienceIntegration:
    def test_analyze_includes_suggested_jobs_field(self):
        with patch.dict("os.environ", {}, clear=True):
            response = client.post(
                "/analyze",
                json={
                    "resume_text": SAMPLE_RESUME,
                    "target_role": "Machine Learning Engineer",
                    "experience_level": "junior",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert "suggested_jobs" in data

    def test_junior_experience_level_is_passed_to_jobs_fetcher(self, monkeypatch):
        captured = {}

        def fake_fetch(role, experience_level=None):
            captured["role"] = role
            captured["experience_level"] = experience_level
            return []

        monkeypatch.setattr("app.analyzer.fetch_relevant_jobs_for_role", fake_fetch)

        with patch.dict("os.environ", {}, clear=True):
            response = client.post(
                "/analyze",
                json={
                    "resume_text": SAMPLE_RESUME,
                    "target_role": "Data Engineer",
                    "experience_level": "junior",
                },
            )

        assert response.status_code == 200
        assert captured["role"] == "Data Engineer"
        assert captured["experience_level"] == "junior"

    def test_roadmap_items_have_certifications_field(self):
        with patch.dict("os.environ", {}, clear=True):
            response = client.post(
                "/analyze",
                json={
                    "resume_text": SAMPLE_RESUME,
                    "target_role": "Machine Learning Engineer",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["roadmap"]
        for item in data["roadmap"]:
            assert "certifications" in item

    def test_junior_job_titles_filter_out_senior_like_roles(self, monkeypatch):
        class DummyJob:
            def __init__(self, title):
                self.title = title
                self.company_name = "TestCo"
                self.location = "Remote"
                self.job_highlights = {}
                self.job_id = "1"

        from app import jobs as jobs_module

        assert jobs_module._title_matches_experience("Senior Data Engineer", "junior") is False
        assert jobs_module._title_matches_experience("Data Engineer", "junior") is True

        def fake_search(*args, **kwargs):
            return {
                "jobs_results": [
                    {
                        "title": "Senior Data Engineer",
                        "company_name": "A",
                        "location": "Remote",
                        "job_id": "1",
                    },
                    {
                        "title": "Data Engineer",
                        "company_name": "B",
                        "location": "Remote",
                        "job_id": "2",
                    },
                ]
            }

        monkeypatch.setattr("app.jobs.GoogleSearch.get_dict", lambda self: fake_search())

        with patch.dict("os.environ", {"SERPAPI_KEY": "dummy"}):
            jobs = jobs_module.fetch_relevant_jobs_for_role("Data Engineer", experience_level="junior")

        for job in jobs:
            assert "senior" not in job.title.lower()

    def test_mock_questions_happy_path_ai(self):
        mock_response_text = """{
            "questions": [
                "What is a REST API?",
                "Explain the CAP theorem.",
                "How would you design a URL shortener?"
            ]
        }"""

        mock_response = MagicMock()
        mock_response.text = mock_response_text

        with patch("app.analyzer.genai.GenerativeModel") as mock_model_cls:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_model_cls.return_value = mock_model

            with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
                response = client.post(
                    "/mock-questions",
                    json={
                        "target_role": "Backend Engineer",
                        "focus_skills": ["Python", "SQL"],
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["target_role"] == "Backend Engineer"
        assert isinstance(data["questions"], list)
        assert len(data["questions"]) > 0
        assert all(isinstance(q, str) and q.strip() for q in data["questions"])

    def test_mock_questions_empty_role_rejected(self):
        response = client.post(
            "/mock-questions",
            json={"target_role": "   "},
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
