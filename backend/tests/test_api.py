"""
Интеграционные тесты API.
Запуск: docker exec deploy-backend-1 python -m pytest tests/ -v
Или локально: cd backend && python -m pytest tests/ -v (при запущенной БД)
"""
import asyncio
import httpx
import pytest

BASE = "http://localhost:8000"


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def client():
    return httpx.Client(base_url=BASE, timeout=30)


@pytest.fixture(scope="module")
def auth_token(client):
    import time
    email = f"test_{int(time.time())}@pytest.com"
    r = client.post("/api/auth/register", json={"email": email, "password": "TestPass123"})
    assert r.status_code == 201, f"Register failed: {r.text}"
    return r.json()["token"]


@pytest.fixture(scope="module")
def headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


# === AUTH ===

class TestAuth:
    def test_register(self, client):
        import time
        r = client.post("/api/auth/register", json={
            "email": f"reg_{int(time.time())}@pytest.com",
            "password": "TestPass123"
        })
        assert r.status_code == 201
        data = r.json()
        assert "token" in data
        assert "user_id" in data

    def test_register_duplicate(self, client, auth_token):
        r = client.post("/api/auth/register", json={
            "email": "duplicate@test.com", "password": "TestPass123"
        })
        r2 = client.post("/api/auth/register", json={
            "email": "duplicate@test.com", "password": "TestPass123"
        })
        assert r2.status_code in (409, 422)

    def test_login_wrong_password(self, client):
        r = client.post("/api/auth/login", json={
            "email": "nonexistent@test.com", "password": "wrong"
        })
        assert r.status_code in (401, 404)

    def test_unauthorized_access(self, client):
        r = client.get("/api/profile")
        assert r.status_code == 401

    def test_invalid_token(self, client):
        r = client.get("/api/profile", headers={"Authorization": "Bearer invalid"})
        assert r.status_code == 401


# === PROFILE ===

class TestProfile:
    def test_get_empty_profile(self, client, headers):
        r = client.get("/api/profile", headers=headers)
        assert r.status_code == 200

    def test_update_profile(self, client, headers):
        r = client.put("/api/profile", headers=headers, json={
            "name": "TestUser",
            "specialization": "backend",
            "experience_level": "junior",
            "skills": "Python, FastAPI",
            "career_goal": "Senior Developer"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "TestUser"
        assert data["specialization"] == "backend"
        assert data["experience_level"] == "junior"

    def test_profile_persists(self, client, headers):
        r = client.get("/api/profile", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert data["specialization"] == "backend"
        assert data["skills"] == "Python, FastAPI"

    def test_get_role(self, client, headers):
        r = client.get("/api/profile/role", headers=headers)
        assert r.status_code == 200
        assert r.json()["role"] == "user"


# === CHATS ===

class TestChats:
    def test_welcome_chats_created(self, client, headers):
        r = client.get("/api/chats/all", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert data["lenItems"] >= 3, "Should have welcome chats"

    def test_get_chat_messages_ordered(self, client, headers):
        chats = client.get("/api/chats/all", headers=headers).json()
        if chats["items"]:
            chat_id = chats["items"][0]["id"]
            r = client.get(f"/api/chats/{chat_id}", headers=headers)
            assert r.status_code == 200
            msgs = r.json()["items"][0]["messages"]
            if len(msgs) >= 2:
                assert msgs[0]["sender_type_id"] == "user", "First message should be from user"
                assert msgs[1]["sender_type_id"] == "chat", "Second message should be from bot"

    def test_rename_chat(self, client, headers):
        chats = client.get("/api/chats/all", headers=headers).json()
        if chats["items"]:
            chat_id = chats["items"][0]["id"]
            r = client.patch(f"/api/chats/{chat_id}", headers=headers, json={"title": "Renamed"})
            assert r.status_code == 200
            assert r.json()["title"] == "Renamed"

    def test_delete_chat(self, client, headers):
        chats = client.get("/api/chats/all", headers=headers).json()
        if not chats["items"]:
            pytest.skip("No chats to delete")
        chat_id = chats["items"][-1]["id"]
        r = client.delete(f"/api/chats/{chat_id}", headers=headers)
        assert r.status_code == 204


# === SURVEYS ===

class TestSurveys:
    def test_list_surveys(self, client, headers):
        r = client.get("/api/surveys", headers=headers)
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_mandatory_pending(self, client, headers):
        r = client.get("/api/surveys/mandatory/pending", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1, "Should have at least 1 mandatory survey"

    def test_get_survey_detail(self, client, headers):
        surveys = client.get("/api/surveys", headers=headers).json()
        r = client.get(f"/api/surveys/{surveys[0]['id']}", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "questions" in data
        assert len(data["questions"]) > 0

    def test_submit_survey(self, client, headers):
        surveys = client.get("/api/surveys/mandatory/pending", headers=headers).json()
        if not surveys:
            pytest.skip("No pending mandatory surveys")

        survey_id = surveys[0]["id"]
        detail = client.get(f"/api/surveys/{survey_id}", headers=headers).json()

        answers = []
        for q in detail["questions"]:
            if q["question_type"] == "text":
                answers.append({"question_id": q["id"], "free_text": "Test answer"})
            elif q["options"]:
                answers.append({"question_id": q["id"], "option_id": q["options"][0]["id"]})

        r = client.post(f"/api/surveys/{survey_id}/submit", headers=headers, json={"answers": answers})
        assert r.status_code == 200, f"Submit failed: {r.text}"
        data = r.json()
        assert data["is_validated"] is True
        assert data["validation_result"] is not None

    def test_get_my_answers(self, client, headers):
        surveys = client.get("/api/surveys", headers=headers).json()
        completed = [s for s in surveys if s["is_completed"]]
        if not completed:
            pytest.skip("No completed surveys")

        r = client.get(f"/api/surveys/{completed[0]['id']}/my-answers", headers=headers)
        assert r.status_code == 200
        assert len(r.json()) > 0

    def test_resubmit_survey(self, client, headers):
        surveys = client.get("/api/surveys", headers=headers).json()
        completed = [s for s in surveys if s["is_completed"]]
        if not completed:
            pytest.skip("No completed surveys")

        survey_id = completed[0]["id"]
        detail = client.get(f"/api/surveys/{survey_id}", headers=headers).json()
        answers = []
        for q in detail["questions"]:
            if q["question_type"] == "text":
                answers.append({"question_id": q["id"], "free_text": "Updated answer"})
            elif q["options"]:
                answers.append({"question_id": q["id"], "option_id": q["options"][-1]["id"]})

        r = client.post(f"/api/surveys/{survey_id}/submit", headers=headers, json={"answers": answers})
        assert r.status_code == 200, f"Resubmit failed: {r.text}"


# === ARTICLES ===

class TestArticles:
    def test_list_categories(self, client, headers):
        r = client.get("/api/articles/categories", headers=headers)
        assert r.status_code == 200
        assert len(r.json()) >= 5

    def test_list_articles(self, client, headers):
        r = client.get("/api/articles", headers=headers)
        assert r.status_code == 200
        assert len(r.json()) >= 7

    def test_filter_by_specialization(self, client, headers):
        r = client.get("/api/articles?specialization=backend", headers=headers)
        assert r.status_code == 200
        for a in r.json():
            assert a["specialization"] in ("backend", None)

    def test_get_article_by_slug(self, client, headers):
        r = client.get("/api/articles/how-to-write-resume", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "content_md" in data
        assert len(data["content_md"]) > 100

    def test_article_not_found(self, client, headers):
        r = client.get("/api/articles/nonexistent-slug", headers=headers)
        assert r.status_code == 404


# === EXPORT ===

class TestExport:
    def test_export_article_md(self, client, headers):
        r = client.post("/api/export/article", headers=headers, json={
            "slug": "how-to-write-resume", "format": "md"
        })
        assert r.status_code == 200
        assert "text/markdown" in r.headers.get("content-type", "")

    def test_export_article_html(self, client, headers):
        r = client.post("/api/export/article", headers=headers, json={
            "slug": "git-basics", "format": "html"
        })
        assert r.status_code == 200
        assert b"<html" in r.content

    def test_export_invalid_format(self, client, headers):
        r = client.post("/api/export/article", headers=headers, json={
            "slug": "git-basics", "format": "pdf"
        })
        assert r.status_code == 400


# === SEARCH ===

class TestSearch:
    def test_search_articles(self, client, headers):
        r = client.get("/api/search?q=резюме", headers=headers)
        assert r.status_code == 200
        results = r.json()
        assert any(r["type"] == "article" for r in results)

    def test_search_short_query(self, client, headers):
        r = client.get("/api/search?q=a", headers=headers)
        assert r.status_code == 200
        assert r.json() == []


# === ROADMAP ===

class TestRoadmap:
    def test_get_progress_empty(self, client, headers):
        r = client.get("/api/roadmap/progress", headers=headers)
        assert r.status_code == 200
        assert r.json() == []

    def test_toggle_progress(self, client, headers):
        r = client.post("/api/roadmap/progress", headers=headers, json={
            "roadmap_key": "backend", "step_id": "1"
        })
        assert r.status_code == 201
        assert r.json()["action"] == "added"

    def test_progress_persists(self, client, headers):
        r = client.get("/api/roadmap/progress?roadmap_key=backend", headers=headers)
        assert r.status_code == 200
        steps = r.json()
        assert any(s["step_id"] == "1" for s in steps)

    def test_untoggle_progress(self, client, headers):
        r = client.post("/api/roadmap/progress", headers=headers, json={
            "roadmap_key": "backend", "step_id": "1"
        })
        assert r.status_code == 201
        assert r.json()["action"] == "removed"


# === RATE LIMITING ===

class TestChangePassword:
    def test_change_password(self, client, headers):
        r = client.post("/api/profile/change-password", headers=headers, json={
            "current_password": "TestPass123",
            "new_password": "NewPass456!"
        })
        assert r.status_code == 200

        # Change back
        r2 = client.post("/api/profile/change-password", headers=headers, json={
            "current_password": "NewPass456!",
            "new_password": "TestPass123"
        })
        assert r2.status_code == 200

    def test_change_password_wrong_current(self, client, headers):
        r = client.post("/api/profile/change-password", headers=headers, json={
            "current_password": "WrongPassword",
            "new_password": "NewPass456!"
        })
        assert r.status_code == 400

    def test_change_password_too_short(self, client, headers):
        r = client.post("/api/profile/change-password", headers=headers, json={
            "current_password": "TestPass123",
            "new_password": "short"
        })
        assert r.status_code == 400


class TestAdminLogin:
    def test_admin_login(self, client):
        r = client.post("/api/auth/login", json={
            "email": "admin@career-helper.ru",
            "password": "Admin123!"
        })
        assert r.status_code == 200
        token = r.json()["token"]
        h = {"Authorization": f"Bearer {token}"}

        role = client.get("/api/profile/role", headers=h).json()
        assert role["role"] == "admin"

    def test_admin_can_list_users(self, client):
        r = client.post("/api/auth/login", json={
            "email": "admin@career-helper.ru",
            "password": "Admin123!"
        })
        token = r.json()["token"]
        h = {"Authorization": f"Bearer {token}"}

        r2 = client.get("/api/admin/users", headers=h)
        assert r2.status_code == 200
        assert len(r2.json()) > 0


class TestSurveyProfileSync:
    def test_profile_filled_after_mandatory_survey(self, client):
        import time
        email = f"sync_{int(time.time())}@pytest.com"
        r = client.post("/api/auth/register", json={"email": email, "password": "TestPass123"})
        token = r.json()["token"]
        h = {"Authorization": f"Bearer {token}"}

        # Profile should be empty
        profile = client.get("/api/profile", headers=h).json()
        assert profile["specialization"] is None

        # Submit mandatory survey
        pending = client.get("/api/surveys/mandatory/pending", headers=h).json()
        if not pending:
            return

        survey = client.get(f"/api/surveys/{pending[0]['id']}", headers=h).json()
        answers = []
        for q in survey["questions"]:
            if q["question_type"] == "text":
                answers.append({"question_id": q["id"], "free_text": "Python, Go"})
            elif q["options"]:
                answers.append({"question_id": q["id"], "option_id": q["options"][0]["id"]})

        client.post(f"/api/surveys/{pending[0]['id']}/submit", headers=h, json={"answers": answers})

        # Profile should be filled from survey
        profile2 = client.get("/api/profile", headers=h).json()
        assert profile2["specialization"] is not None or profile2["experience_level"] is not None


class TestSecurity:
    def test_rate_limit_not_triggered_on_normal_use(self, client, headers):
        for _ in range(5):
            r = client.get("/api/profile", headers=headers)
            assert r.status_code == 200
