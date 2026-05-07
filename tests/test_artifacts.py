"""Тесты /api/v1/artifacts/*"""
import io
import uuid
import pytest
from httpx import AsyncClient
from tests.factories import create_project, create_team, create_meeting, uid

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/artifacts"


async def create_link_artifact(client: AsyncClient, **overrides) -> dict:
    payload = {
        "name": f"Ссылка_{uid()}",
        "type": "LINK",
        "url": "https://example.com/resource",
        **overrides,
    }
    resp = await client.post(f"{BASE}/link", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ===========================================================================

class TestCreateLinkArtifact:
    async def test_create_link(self, auth_client: AsyncClient):
        resp = await auth_client.post(f"{BASE}/link", json={
            "name": f"Ссылка_{uid()}",
            "type": "LINK",
            "url": "https://example.com",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert "id" in body
        assert body["type"] == "LINK"
        assert body["url"] == "https://example.com"

    async def test_create_link_attached_to_project(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        resp = await auth_client.post(f"{BASE}/link", json={
            "name": f"Ссылка_{uid()}",
            "type": "LINK",
            "url": "https://figma.com/design",
            "project_id": project["id"],
        })
        assert resp.status_code == 201

    async def test_create_link_attached_to_meeting(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        meeting = await create_meeting(auth_client, team["id"])
        resp = await auth_client.post(f"{BASE}/link", json={
            "name": f"Ссылка_{uid()}",
            "type": "LINK",
            "url": "https://docs.google.com/doc",
            "meeting_id": meeting["id"],
        })
        assert resp.status_code == 201

    async def test_create_requires_auth(self, client: AsyncClient):
        resp = await client.post(f"{BASE}/link", json={
            "name": "Test",
            "type": "LINK",
            "url": "https://example.com",
        })
        assert resp.status_code == 401


class TestUploadFileArtifact:
    async def test_upload_file(self, auth_client: AsyncClient):
        file_content = b"Hello, this is test file content"
        resp = await auth_client.post(
            f"{BASE}/upload",
            files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")},
            data={"name": f"Файл_{uid()}", "description": "Тестовый файл"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert "id" in body
        assert body["type"] == "FILE"
        assert body["url"] is not None  # должна быть S3 ссылка

    async def test_upload_without_name_uses_filename(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            f"{BASE}/upload",
            files={"file": ("myfile.pdf", io.BytesIO(b"%PDF content"), "application/pdf")},
        )
        assert resp.status_code == 201
        # name должно быть myfile.pdf или похожее
        body = resp.json()
        assert "myfile" in body["name"].lower() or body["name"]

    async def test_upload_attached_to_project(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        resp = await auth_client.post(
            f"{BASE}/upload",
            files={"file": ("doc.txt", io.BytesIO(b"content"), "text/plain")},
            data={"project_id": project["id"]},
        )
        assert resp.status_code == 201


class TestGetArtifact:
    async def test_get_by_id(self, auth_client: AsyncClient):
        artifact = await create_link_artifact(auth_client)
        resp = await auth_client.get(f"{BASE}/{artifact['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == artifact["id"]

    async def test_get_nonexistent(self, auth_client: AsyncClient):
        resp = await auth_client.get(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestUpdateArtifact:
    async def test_update_name(self, auth_client: AsyncClient):
        artifact = await create_link_artifact(auth_client)
        new_name = f"Обновлённое_{uid()}"
        resp = await auth_client.patch(
            f"{BASE}/{artifact['id']}",
            json={"name": new_name},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == new_name

    async def test_update_description(self, auth_client: AsyncClient):
        artifact = await create_link_artifact(auth_client)
        resp = await auth_client.patch(
            f"{BASE}/{artifact['id']}",
            json={"description": "Новое описание"},
        )
        assert resp.status_code == 200
        assert resp.json()["description"] == "Новое описание"

    async def test_update_nonexistent(self, auth_client: AsyncClient):
        resp = await auth_client.patch(
            f"{BASE}/{uuid.uuid4()}",
            json={"name": "Test"},
        )
        assert resp.status_code == 404


class TestDeleteArtifact:
    async def test_delete_success(self, auth_client: AsyncClient):
        artifact = await create_link_artifact(auth_client)
        resp = await auth_client.delete(f"{BASE}/{artifact['id']}")
        assert resp.status_code == 204

        resp2 = await auth_client.get(f"{BASE}/{artifact['id']}")
        assert resp2.status_code == 404

    async def test_delete_nonexistent(self, auth_client: AsyncClient):
        resp = await auth_client.delete(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestArtifactProjectBinding:
    async def test_attach_to_project(self, auth_client: AsyncClient):
        artifact = await create_link_artifact(auth_client)
        project = await create_project(auth_client)

        resp = await auth_client.post(f"{BASE}/{artifact['id']}/projects/{project['id']}")
        assert resp.status_code == 204

    async def test_detach_from_project(self, auth_client: AsyncClient):
        project = await create_project(auth_client)
        artifact = await create_link_artifact(auth_client, project_id=project["id"])

        resp = await auth_client.delete(f"{BASE}/{artifact['id']}/projects/{project['id']}")
        assert resp.status_code == 204


class TestArtifactMeetingBinding:
    async def test_attach_to_meeting(self, auth_client: AsyncClient):
        artifact = await create_link_artifact(auth_client)
        team = await create_team(auth_client)
        meeting = await create_meeting(auth_client, team["id"])

        resp = await auth_client.post(f"{BASE}/{artifact['id']}/meetings/{meeting['id']}")
        assert resp.status_code == 204

    async def test_detach_from_meeting(self, auth_client: AsyncClient):
        team = await create_team(auth_client)
        meeting = await create_meeting(auth_client, team["id"])
        artifact = await create_link_artifact(auth_client, meeting_id=meeting["id"])

        resp = await auth_client.delete(f"{BASE}/{artifact['id']}/meetings/{meeting['id']}")
        assert resp.status_code == 204
