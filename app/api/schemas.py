"""Pydantic schemas for the FastAPI presentation and API layer."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.defender.models import SecurityAlert, SecurityAnalysisResult, SecurityEvent
from app.simulator.models import WarehouseObservation


class HealthResponse(BaseModel):
    """Service health and component readiness response."""

    status: str = Field(default="healthy", description="Overall service operational health")
    service: str = Field(default="organization-security-platform", description="Service identifier")
    simulator: str = Field(default="running", description="Status of the cold-storage simulator")
    defender: str = Field(default="ready", description="Status of the DefenderService pipeline")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp of health check",
    )


class WarehouseStepResponse(BaseModel):
    """Response returned when the warehouse simulation advances by one step."""

    observation: WarehouseObservation = Field(..., description="Newly generated warehouse observation")
    security_analysis: SecurityAnalysisResult = Field(..., description="Actual security pipeline evaluation")


class SecurityStatusResponse(BaseModel):
    """Overall organization security status summary."""

    status: str = Field(..., description="Classification: NORMAL, LOW, SUSPICIOUS, POTENTIAL_ATTACK, COORDINATED_ATTACK")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Composite risk probability")
    integrity_score: float = Field(..., ge=0.0, le=100.0, description="System integrity percentage")
    active_alerts: int = Field(..., ge=0, description="Count of currently unresolved security alerts")
    sources: int = Field(default=5, description="Number of active organizational data sources")
    last_analysis_timestamp: Optional[str] = Field(None, description="Timestamp of latest security evaluation")
    backend_health: str = Field(default="ONLINE", description="Defender backend connectivity status")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp of query",
    )


class ResetResponse(BaseModel):
    """Response returned upon system reset."""

    success: bool = Field(default=True)
    message: str = Field(default="Simulator and DefenderService successfully reset to baseline.")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ScenarioInfo(BaseModel):
    """Metadata describing an available deterministic attack scenario."""

    id: str = Field(..., description="Scenario identifier used in API endpoints")
    name: str = Field(..., description="Human-readable scenario title")
    description: str = Field(..., description="Details of attack vector and affected operational parameters")
    target_constraint: str = Field(..., description="Primary constraint targeted (C1, C2, C3, Multi-Source)")


class ScenariosListResponse(BaseModel):
    """List of all registered deterministic attack scenarios."""

    scenarios: List[ScenarioInfo]


class ScenarioExecutionResponse(BaseModel):
    """Response returned after executing a deterministic attack scenario."""

    scenario: str = Field(..., description="Identifier of executed attack scenario")
    observation: WarehouseObservation = Field(..., description="Manipulated observation fed to defender")
    security_analysis: SecurityAnalysisResult = Field(..., description="Real pipeline analysis result")
