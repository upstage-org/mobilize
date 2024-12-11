from faker import Faker
import pytest
from authentication.tests.auth_test import TestAuthenticationController
from src.main import app
from users.db_models.user import SUPER_ADMIN
from upstage_options.http.schema import config_graphql_app

app.mount("/config_graphql", config_graphql_app)
test_AuthenticationController = TestAuthenticationController()


@pytest.mark.anyio
class TestUpStageOptionsController:
    async def test_01_nginx_config(self, client):
        query = "{ nginx { limit } }"
        response = client.post("/config_graphql", json={"query": query})
        assert response.status_code == 200
        assert "nginx" in response.json()["data"]
        assert "limit" in response.json()["data"]["nginx"]

    async def test_02_system_info(self, client):
        query = """
        {
            system {
                termsOfService {
                    id
                    name
                    value
                    createdOn
                }
                manual {
                    id
                    name
                    value
                     createdOn
                }
                esp {
                    id
                    name
                    value
                    createdOn
                }
                enableDonate {
                    id
                    name
                    value
                    createdOn
                }
            }
        }
        """
        response = client.post("/config_graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()["data"]["system"]
        assert "termsOfService" in data
        assert "manual" in data
        assert "esp" in data
        assert "enableDonate" in data
        assert "errors" not in response.json()

    async def test_03_foyer_info(self, client):
        query = """
        {
            foyer {
                title {
                    id
                    name
                    value
                    createdOn
                }
                description {
                    id
                    name
                    value
                    createdOn
                }
                menu {
                    id
                    name
                    value
                    createdOn
                }
                showRegistration {
                    id
                    name
                    value
                    createdOn
                }
            }
        }
        """
        response = client.post("/config_graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()["data"]["foyer"]
        assert "title" in data
        assert "description" in data
        assert "menu" in data
        assert "showRegistration" in data
        assert "errors" not in response.json()

    async def test_04_update_terms_of_service(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        query = """
        mutation {
            updateTermsOfService(url: "https://www.example.com") {
                id
                name
                value
                createdOn
            }
        }
        """
        response = client.post(
            "/config_graphql", json={"query": query}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()["data"]["updateTermsOfService"]
        assert "id" in data
        assert "name" in data
        assert "value" in data
        assert "createdOn" in data
        assert "errors" not in response.json()

        query = """
            mutation {
                updateTermsOfService(url: "https://www.test.com") {
                    id
                    name
                    value
                    createdOn
                }
            }
        """
        response = client.post(
            "/config_graphql", json={"query": query}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()["data"]["updateTermsOfService"]
        assert "id" in data
        assert "name" in data
        assert "value" in data
        assert "createdOn" in data
        assert "errors" not in response.json()

    async def test_05_save_config(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        query = """
            mutation {
                saveConfig(input: {name: "test", value: "test"}) {
                    id
                    name
                    value
                    createdOn
                }
            }
        """
        response = client.post(
            "/config_graphql", json={"query": query}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()["data"]["saveConfig"]
        assert "id" in data
        assert "name" in data
        assert "value" in data
        assert "createdOn" in data
        assert "errors" not in response.json()

        query = """
            mutation {
                saveConfig(input: {name: "test", value: "test2"}) {
                    id
                    name
                    value
                    createdOn
                }
            }
        """
        response = client.post(
            "/config_graphql", json={"query": query}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()["data"]["saveConfig"]
        assert "id" in data
        assert "name" in data
        assert "value" in data
        assert "createdOn" in data
        assert "errors" not in response.json()

    async def test_06_send_email(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        query = """
            mutation ($input: SystemEmailInput!) {
                sendSystemEmail(input: $input) {
                    success
                }   
            }
        """

        variables = {
            "input": {
                "subject": "Test",
                "body": "Test",
                "recipients": Faker().email(),
                "bcc": Faker().email(),
            }
        }

        response = client.post(
            "/config_graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()["data"]["sendSystemEmail"]
        assert "success" in data
        assert "errors" not in response.json()
