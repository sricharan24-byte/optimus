"""Warehouse operational telemetry API endpoints."""

from fastapi import APIRouter
from app.api.schemas import WarehouseStepResponse
from app.api.state import app_state
from app.simulator.models import WarehouseObservation

router = APIRouter(prefix="/warehouse", tags=["Warehouse"])


@router.get("/current", response_model=WarehouseObservation)
def get_current_warehouse_state() -> WarehouseObservation:
    """Retrieve the current real-time cold-storage warehouse telemetry and operational state."""
    return app_state.warehouse.get_current_observation()


@router.post("/step", response_model=WarehouseStepResponse)
def step_warehouse_simulation() -> WarehouseStepResponse:
    """Advance the warehouse simulation by one discrete step and evaluate through DefenderService.
    
    The newly generated observation is processed immediately by the full security pipeline,
    updating the security state, events, and active alerts atomically.
    """
    observation, security_analysis = app_state.step()

    return WarehouseStepResponse(
        observation=observation,
        security_analysis=security_analysis,
    )
