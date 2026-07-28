"""Tests für ats_cleanjson.py — ein Basis-Adapter, sechs JSON-Profile."""
from ats_adapters import ats_cleanjson as ac


def test_greenhouse_mapping():
    payload = {"jobs": [{
        "id": 123, "title": "Working Student Software (m/f/d)",
        "absolute_url": "https://boards.greenhouse.io/acme/jobs/123",
        "location": {"name": "Munich, Germany"},
        "updated_at": "2026-07-20T10:00:00-04:00",
        "content": "&lt;p&gt;Python und Docker&lt;/p&gt;",
    }]}
    jobs = ac.parse("greenhouse", payload, company="Acme")
    j = jobs[0]
    assert j["_source"] == "ats_greenhouse"
    assert j["job_id"] == "123"
    assert j["title"].startswith("Working Student")
    assert j["location"] == "Munich, Germany"
    assert j["posted_at"] == "2026-07-20"
    assert "Python" in j["description"] and "<p>" not in j["description"]
    assert j["url"] == "https://boards.greenhouse.io/acme/jobs/123"


def test_lever_mapping():
    payload = [{
        "id": "abc-def", "text": "Working Student Backend",
        "hostedUrl": "https://jobs.lever.co/acme/abc-def",
        "categories": {"location": "Munich", "commitment": "Part-time"},
        "createdAt": 1784739785000,
        "descriptionPlain": "Go und Kubernetes",
    }]
    j = ac.parse("lever", payload, company="Acme")[0]
    assert j["_source"] == "ats_lever"
    assert j["title"] == "Working Student Backend"
    assert j["location"] == "Munich"
    assert j["employment_hint"] == "Part-time"
    assert j["posted_at"] == "2026-07-22"
    assert j["url"].endswith("abc-def")


def test_ashby_mapping():
    payload = {"jobs": [{
        "id": "uuid-1", "title": "Software Engineer Intern",
        "location": "Remote - Germany", "employmentType": "Intern",
        "publishedAt": "2026-07-18T00:00:00Z",
        "jobUrl": "https://jobs.ashbyhq.com/acme/uuid-1",
        "descriptionHtml": "<p>TypeScript</p>",
        "isRemote": True,
    }]}
    j = ac.parse("ashby", payload, company="Acme")[0]
    assert j["_source"] == "ats_ashby"
    assert j["location"] == "Remote - Germany"
    assert j["posted_at"] == "2026-07-18"
    assert "TypeScript" in j["description"]


def test_recruitee_mapping():
    payload = {"offers": [{
        "id": 55, "title": "Working Student DevOps",
        "careers_url": "https://acme.recruitee.com/o/working-student-devops",
        "location": "Munich, Deutschland", "employment_type_code": "part_time",
        "created_at": "2026-07-15 09:30:00 UTC",
        "description": "<p>CI/CD</p>",
    }]}
    j = ac.parse("recruitee", payload, company="Acme")[0]
    assert j["_source"] == "ats_recruitee"
    assert j["posted_at"] == "2026-07-15"
    assert j["url"].endswith("working-student-devops")


def test_smartrecruiters_mapping():
    payload = {"content": [{
        "id": "744", "name": "Working Student IT",
        "location": {"city": "Munich", "country": "de"},
        "releasedDate": "2026-07-19T07:00:00.000Z",
        "ref": "https://api.smartrecruiters.com/v1/companies/Acme/postings/744",
        "applyUrl": "https://jobs.smartrecruiters.com/Acme/744",
    }]}
    j = ac.parse("smartrecruiters", payload, company="Acme")[0]
    assert j["_source"] == "ats_smartrecruiters"
    assert j["location"] == "Munich"
    assert j["posted_at"] == "2026-07-19"
    assert j["url"] == "https://jobs.smartrecruiters.com/Acme/744"


def test_workday_mapping():
    payload = {"jobPostings": [{
        "title": "Working Student Software (m/f/d)",
        "externalPath": "/job/Munich/Working-Student-Software_R123",
        "locationsText": "Munich", "postedOn": "Vor 5 Tagen gepostet",
        "bulletFields": ["R123"],
    }]}
    j = ac.parse("workday", payload, company="ExampleCorp",
                 slug="examplecorp.wd3/ExampleCorp")[0]
    assert j["_source"] == "ats_workday"
    assert j["job_id"] == "R123"
    assert j["location"] == "Munich"
    assert j["url"] == ("https://examplecorp.wd3.myworkdayjobs.com/de-DE/ExampleCorp"
                        "/job/Munich/Working-Student-Software_R123")


def test_unknown_profile_raises():
    import pytest
    with pytest.raises(KeyError):
        ac.parse("gibtsnicht", {}, company="X")
