"""Tests for Live Operations & Sensor Monitor (/operations) and Warehouse History API."""

import re
import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.api.state import app_state


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_before_each():
    """Ensure every test starts with a clean baseline state."""
    app_state.reset()


class TestOperationsMonitor:
    """Test suite for the Live Operations & Sensor Monitor page and history API."""

    def test_operations_page_loads(self, client):
        """Verify /operations loads correctly with required structure and title."""
        response = client.get("/operations")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        html = response.text

        # Core required titles & subtitles
        assert "Live Operations & Sensor Monitor" in html
        assert "Simulated IoT Environment" in html
        assert "SIMULATED FACILITY" in html

        # Sections
        assert "Environmental IoT Sensors" in html
        assert "Inventory & Storage Capacity" in html
        assert "Shipment Flow Ledgers" in html
        assert "Operational History Trends" in html
        assert "Recent Simulated Readings" in html

        # Key DOM hooks
        assert 'id="ops-temp"' in html
        assert 'id="ops-humidity"' in html
        assert 'id="ops-occupancy"' in html
        assert 'id="ops-inventory"' in html
        assert 'id="ops-free-capacity"' in html
        assert 'id="ops-total-capacity"' in html
        assert 'id="ops-inbound"' in html
        assert 'id="ops-outbound"' in html
        assert 'id="btn-ops-step"' in html
        assert 'id="btn-ops-reset"' in html
        assert 'id="ops-history-tbody"' in html

    def test_operations_serves_js_application(self, client):
        """Verify static delivery of operations.js client."""
        response = client.get("/js/operations.js")
        assert response.status_code == 200
        assert "javascript" in response.headers.get("content-type", "")
        assert "refreshOperations" in response.text
        assert "renderSvgChart" in response.text

    def test_warehouse_history_returns_actual_history(self, client):
        """Verify /api/warehouse/history returns actual historical observations."""
        response = client.get("/api/warehouse/history")
        assert response.status_code == 200
        data = response.json()

        assert data["warehouse"] == "W01"
        assert "observations" in data
        assert isinstance(data["observations"], list)
        assert len(data["observations"]) >= 1

        first_obs = data["observations"][0]
        assert "step" in first_obs
        assert "timestamp" in first_obs
        assert "temperature" in first_obs
        assert "humidity" in first_obs
        assert "inventory" in first_obs
        assert "free_capacity" in first_obs
        assert "total_capacity" in first_obs
        assert "occupancy" in first_obs
        assert "inbound" in first_obs
        assert "outbound" in first_obs

        assert first_obs["step"] == 0
        assert first_obs["inventory"] == 42.0
        assert first_obs["free_capacity"] == 8.0
        assert first_obs["total_capacity"] == 50.0

    def test_history_endpoint_does_not_advance_simulation(self, client):
        """Verify that polling /api/warehouse/history never advances simulation step."""
        initial_step = app_state.warehouse.step_count

        for _ in range(5):
            res = client.get("/api/warehouse/history")
            assert res.status_code == 200

        assert app_state.warehouse.step_count == initial_step

    def test_step_advances_operations_data_exactly_one_step(self, client):
        """Verify that stepping advances simulation and reflects in history."""
        # Initial step
        init_history = client.get("/api/warehouse/history").json()
        init_len = len(init_history["observations"])

        # Execute step
        step_res = client.post("/api/warehouse/step")
        assert step_res.status_code == 200
        step_data = step_res.json()
        assert step_data["observation"]["step"] == 1

        # Check history
        updated_history = client.get("/api/warehouse/history").json()
        assert len(updated_history["observations"]) == init_len + 1
        last_obs = updated_history["observations"][-1]
        assert last_obs["step"] == 1
        assert last_obs["total_capacity"] == 50.0

    def test_reset_returns_to_baseline(self, client):
        """Verify that reset restores simulator and history to baseline Step 0."""
        # Advance 3 steps
        for _ in range(3):
            client.post("/api/warehouse/step")

        history_before = client.get("/api/warehouse/history").json()
        assert len(history_before["observations"]) == 4

        # Reset
        reset_res = client.post("/api/security/reset")
        assert reset_res.status_code == 200

        # Verify baseline
        curr_res = client.get("/api/warehouse/current")
        assert curr_res.status_code == 200
        curr = curr_res.json()
        assert curr["step"] == 0
        assert curr["inventory"] == 42.0

        history_after = client.get("/api/warehouse/history").json()
        assert len(history_after["observations"]) == 1
        assert history_after["observations"][0]["step"] == 0

    def test_navigation_links_work(self, client):
        """Verify reciprocal navigation links exist between Security Portal and Operations Monitor."""
        # Security Portal (/) contains link to Operations Monitor (/operations)
        portal_res = client.get("/")
        assert portal_res.status_code == 200
        assert 'href="/operations"' in portal_res.text
        assert "Operations Monitor" in portal_res.text

        # Operations Monitor (/operations) contains link to Security Portal (/)
        ops_res = client.get("/operations")
        assert ops_res.status_code == 200
        assert 'href="/"' in ops_res.text
        assert "Security Portal" in ops_res.text

    def test_all_operations_javascript_dom_ids_exist(self, client):
        """Verify that every DOM ID queried by operations.js exists in operations.html."""
        html_resp = client.get("/operations")
        assert html_resp.status_code == 200
        html = html_resp.text

        js_resp = client.get("/js/operations.js")
        assert js_resp.status_code == 200
        js = js_resp.text

        queried_ids = re.findall(r'getElementById\([\'"]([^\'"]+)[\'"]\)', js)
        assert len(queried_ids) >= 20

        missing_ids = [elem_id for elem_id in queried_ids if f'id="{elem_id}"' not in html]
        assert missing_ids == [], f"DOM IDs queried in operations.js missing in operations.html: {missing_ids}"
