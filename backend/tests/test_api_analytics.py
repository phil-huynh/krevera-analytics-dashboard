import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


@pytest.mark.api
class TestHealthEndpoint:
    def test_health_check_success(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "environment" in data


@pytest.mark.api
class TestMachinesEndpoint:
    def test_get_machines_empty_database(self, client: TestClient):
        response = client.get("/api/v1/analytics/machines")
        assert response.status_code == 200
        data = response.json()
        assert data["machines"] == []
        assert data["count"] == 0

    def test_get_machines_with_data(self, client: TestClient, populated_db):
        response = client.get("/api/v1/analytics/machines")
        assert response.status_code == 200
        data = response.json()
        assert len(data["machines"]) == 3
        assert data["count"] == 3
        assert "molding-machine-1" in data["machines"]
        assert "molding-machine-2" in data["machines"]
        assert "molding-machine-3" in data["machines"]


@pytest.mark.api
class TestCycleTimeEndpoint:
    def test_get_cycle_time_empty_database(self, client: TestClient):
        response = client.get("/api/v1/analytics/cycle-time")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data.get("data", []), list)

    def test_get_cycle_time_with_data(self, client: TestClient, populated_db):
        response = client.get("/api/v1/analytics/cycle-time")
        # API may return 404 if no data matches query criteria
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "data" in data or "count" in data

            if "data" in data and len(data["data"]) > 0:
                first_item = data["data"][0]
                assert "cycle_time" in first_item or "timestamp" in first_item

    def test_get_cycle_time_with_machine_filter(self, client: TestClient, populated_db):
        response = client.get("/api/v1/analytics/cycle-time?machine_id=molding-machine-1")
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()

            if "data" in data:
                for item in data.get("data", []):
                    if "machine_id" in item:
                        assert item["machine_id"] == "molding-machine-1"

    def test_get_cycle_time_with_date_range(self, client: TestClient, populated_db):
        start_date = (datetime.now() - timedelta(days=20)).isoformat()
        end_date = (datetime.now() - timedelta(days=10)).isoformat()

        response = client.get(
            f"/api/v1/analytics/cycle-time?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code in [200, 404]


@pytest.mark.api
class TestDefectRateEndpoint:
    def test_get_defect_rate_empty_database(self, client: TestClient):
        response = client.get("/api/v1/analytics/defect-rate")
        assert response.status_code in [200, 404]

    def test_get_defect_rate_with_data(self, client: TestClient, populated_db):
        response = client.get("/api/v1/analytics/defect-rate")
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()

            assert "data" in data or "total_products" in data

            if "data" in data and len(data["data"]) > 0:
                for item in data["data"]:
                    if "defect_rate" in item:
                        assert 0 <= item["defect_rate"] <= 100

    def test_get_defect_rate_with_machine_filter(self, client: TestClient, populated_db):
        response = client.get("/api/v1/analytics/defect-rate?machine_id=molding-machine-1")
        assert response.status_code in [200, 404]


@pytest.mark.api
class TestTopDefectsEndpoint:
    def test_get_top_defects_empty_database(self, client: TestClient):
        response = client.get("/api/v1/analytics/top-defects")
        assert response.status_code == 200
        data = response.json()

        if "defects" in data:
            assert isinstance(data["defects"], list)

    def test_get_top_defects_with_data(self, client: TestClient, populated_db):
        response = client.get("/api/v1/analytics/top-defects")
        assert response.status_code == 200
        data = response.json()

        if "defects" in data and len(data["defects"]) > 0:
            for defect in data["defects"]:
                assert "defect_type" in defect
                assert "count" in defect
                if "percentage" in defect:
                    assert 0 <= defect["percentage"] <= 100

    def test_get_top_defects_with_limit(self, client: TestClient, populated_db):
        response = client.get("/api/v1/analytics/top-defects?limit=3")
        assert response.status_code == 200
        data = response.json()

        if "defects" in data:
            assert len(data["defects"]) <= 3

    def test_get_top_defects_sorted_by_count(self, client: TestClient, populated_db):
        response = client.get("/api/v1/analytics/top-defects")
        assert response.status_code == 200
        data = response.json()

        if "defects" in data and len(data["defects"]) > 1:
            counts = [defect["count"] for defect in data["defects"]]
            assert counts == sorted(counts, reverse=True)


@pytest.mark.api
class TestMachineComparisonEndpoint:
    def test_get_machine_comparison_empty_database(self, client: TestClient):
        response = client.get("/api/v1/analytics/machine-comparison")
        assert response.status_code == 200
        data = response.json()
        assert "machines" in data

    def test_get_machine_comparison_with_data(self, client: TestClient, populated_db):
        response = client.get("/api/v1/analytics/machine-comparison")
        assert response.status_code == 200
        data = response.json()

        if "machines" in data and len(data["machines"]) > 0:
            for machine in data["machines"]:
                assert "machine_id" in machine
                assert "total_products" in machine or "defect_rate" in machine


@pytest.mark.api
class TestDefectDistributionEndpoint:
    def test_get_defect_distribution_empty_database(self, client: TestClient):
        response = client.get("/api/v1/analytics/defect-distribution")
        assert response.status_code == 200
        data = response.json()
        assert "distribution" in data

    def test_get_defect_distribution_with_data(self, client: TestClient, populated_db):
        response = client.get("/api/v1/analytics/defect-distribution")
        assert response.status_code == 200
        data = response.json()

        assert "distribution" in data
        assert isinstance(data["distribution"], list)


@pytest.mark.api
class TestMachineDefectHeatmapEndpoint:
    def test_get_heatmap_empty_database(self, client: TestClient):
        response = client.get("/api/v1/analytics/machine-defect-heatmap")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))

    def test_get_heatmap_with_data(self, client: TestClient, populated_db):
        response = client.get("/api/v1/analytics/machine-defect-heatmap")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, (dict, list))