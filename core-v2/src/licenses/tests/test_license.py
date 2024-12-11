import pytest
from assets.db_models.asset import AssetModel
from assets.tests.asset_test import TestAssetController
from assets.db_models.asset_license import AssetLicenseModel
from src.main import app
from licenses.http.schema import license_graphql_app
from global_config import DBSession

app.mount("/license_graphql", license_graphql_app)
test_AssetController = TestAssetController()


@pytest.mark.anyio
class TestLicenseController:
    async def test_01_create_license(self, client):
        await test_AssetController.test_03_save_media_successfully(client)
        asset = DBSession.query(AssetModel).first()
        query = """
        mutation ($input: LicenseInput!) {
          createLicense(input: $input) {
            assetId
            level
            permissions
            assetPath
          }
        }
        """
        variables = {
            "input": {
                "assetId": asset.id,
                "level": 1,
                "permissions": "{}",
            }
        }

        response = client.post(
            "/license_graphql", json={"query": query, "variables": variables}
        )
        assert response.status_code == 200
        assert response.json()["data"]["createLicense"]["assetId"] == str(asset.id)
        assert response.json()["data"]["createLicense"]["level"] == 1
        assert response.json()["data"]["createLicense"]["permissions"] == "{}"
        assert response.json()["data"]["createLicense"]["assetPath"] is not None

    async def test_02_revoke_license(self, client):
        license = DBSession.query(AssetLicenseModel).first()
        query = """
            mutation($id: ID!) {
                revokeLicense(id: $id)
            }
        """

        variables = {"id": license.id}

        response = client.post(
            "/license_graphql", json={"query": query, "variables": variables}
        )
        assert response.status_code == 200
        assert response.json()["data"]["revokeLicense"] == "License revoked {}".format(
            license.id
        )

        response = client.post(
            "/license_graphql", json={"query": query, "variables": variables}
        )
        assert response.status_code == 200
        assert response.json()["data"][
            "revokeLicense"
        ] == "Failed to revoke license {}".format(license.id)
        license = DBSession.query(AssetLicenseModel).filter_by(id=license.id).first()
        assert license is None
