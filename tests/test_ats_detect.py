"""Tests für ats_detect.py — ATS-Signaturen erkennen (Spez §3)."""
from ats_adapters import ats_detect as ad


def test_detect_personio():
    html = '<a href="https://acme-gmbh.jobs.personio.de/">Karriere</a>'
    assert ad.detect_from_text(html) == ("personio", "acme-gmbh")


def test_detect_personio_com_migrated():
    html = '<iframe src="https://acme.jobs.personio.com/embed"></iframe>'
    assert ad.detect_from_text(html) == ("personio", "acme")


def test_detect_greenhouse_board_and_embed():
    assert ad.detect_from_text('href="https://boards.greenhouse.io/acme-oss"') == \
        ("greenhouse", "acme-oss")
    assert ad.detect_from_text(
        'src="https://boards.greenhouse.io/embed/job_board?for=acme-pay"') == \
        ("greenhouse", "acme-pay")


def test_detect_lever():
    assert ad.detect_from_text('href="https://jobs.lever.co/acme-media?x=1"') == \
        ("lever", "acme-media")


def test_detect_ashby_recruitee_smartrecruiters_teamtailor():
    assert ad.detect_from_text('href="https://jobs.ashbyhq.com/acme-tools"') == \
        ("ashby", "acme-tools")
    assert ad.detect_from_text('href="https://acme.recruitee.com/o/dev"') == \
        ("recruitee", "acme")
    assert ad.detect_from_text('href="https://jobs.smartrecruiters.com/ExampleGroup/123"') == \
        ("smartrecruiters", "ExampleGroup")
    assert ad.detect_from_text('href="https://acme.teamtailor.com/jobs"') == \
        ("teamtailor", "acme")


def test_detect_workday_three_part_slug():
    html = 'href="https://examplecorp.wd3.myworkdayjobs.com/de-DE/ExampleCorp/job/x"'
    assert ad.detect_from_text(html) == ("workday", "examplecorp.wd3/ExampleCorp")


def test_detect_nothing():
    assert ad.detect_from_text("<html>Wir stellen ein! karriere@acme.de</html>") is None


def test_detect_ignores_own_subdomain_noise():
    # www.jobs.personio.de wäre kein Firmen-Slug
    assert ad.detect_from_text('href="https://www.jobs.personio.de/"') is None


def test_career_links_absolute_and_filtered():
    html = ('<a href="/karriere">Karriere</a>'
            '<a href="https://acme.de/jobs/">Jobs</a>'
            '<a href="/impressum">Impressum</a>'
            '<a href="/career">Career</a>')
    links = ad.career_links(html, base_url="https://acme.de")
    assert "https://acme.de/karriere" in links
    assert "https://acme.de/jobs/" in links
    assert "https://acme.de/career" in links
    assert all("impressum" not in l for l in links)


def test_feed_url_for():
    assert ad.feed_url_for("personio", "acme") == "https://acme.jobs.personio.de/xml"
    assert ad.feed_url_for("greenhouse", "acme-oss") == \
        "https://boards-api.greenhouse.io/v1/boards/acme-oss/jobs?content=true"
    assert ad.feed_url_for("workday", "examplecorp.wd3/ExampleCorp").startswith(
        "https://examplecorp.wd3.myworkdayjobs.com/wday/cxs/examplecorp/ExampleCorp/jobs")
