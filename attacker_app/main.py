"""FastAPI Web Server for Part 2 AI Attacker Application.

Runs independently on port 8001. Interacts with Part 1 exclusively via HTTP.
Serves the Attacker Console UI and provides API endpoints for proposal generation,
human-in-the-loop approval, and execution.
"""

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from attacker_app.gateway_client import GatewayClientError
from attacker_app.schemas import (
    AttackFeedback,
    AttackProposal,
    AttackerHistoryItem,
    AttackerObservation,
    ProposalGenerationRequest,
    ProposalValidationResult,
)
from attacker_app.state import attacker_state

logger = logging.getLogger("attacker.api")

app = FastAPI(
    title="AI Attacker & Adversarial Evaluation Console",
    description="Part 2 Adversarial Application for evaluating Organization Defender System.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def serve_attacker_portal():
    """Serve the standalone Attacker Console UI."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attacker portal frontend file not found.",
        )
    return FileResponse(index_file, media_type="text/html")


@app.get("/api/attacker/status")
def get_attacker_status():
    """Check connectivity to Part 1 gateway and local state summary."""
    connected = False
    gateway_err = None
    try:
        attacker_state.fetch_observation()
        connected = True
    except Exception as e:
        gateway_err = str(e)

    return {
        "status": "online",
        "gateway_connected": connected,
        "gateway_error": gateway_err,
        "has_pending_proposal": attacker_state.pending_proposal is not None,
        "pending_proposal": attacker_state.pending_proposal.model_dump() if attacker_state.pending_proposal else None,
        "pending_proposal_id": attacker_state.pending_proposal_id,
        "pending_planner_label": attacker_state.pending_planner_label,
        "pending_strategy_rationale": attacker_state.pending_strategy_rationale,
        "pending_observed_telemetry": attacker_state.pending_observed_telemetry.model_dump() if attacker_state.pending_observed_telemetry else None,
        "pending_validation": attacker_state.pending_validation.model_dump() if attacker_state.pending_validation else None,
        "history_count": len(attacker_state.history),
        "experiments_count": len(attacker_state.experiments),
    }


@app.get("/api/attacker/observation", response_model=AttackerObservation)
def get_observation():
    """Fetch current restricted operational observation from the Part 1 gateway."""
    try:
        return attacker_state.fetch_observation()
    except GatewayClientError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch observation from Attack Gateway: {e}",
        )


@app.post("/api/attacker/propose")
def generate_attack_proposal(req: ProposalGenerationRequest):
    """Generate candidate attack proposal via selected planner without executing."""
    try:
        (
            proposal,
            validation,
            planner_label,
            strategy_rationale,
            observed_telemetry,
        ) = attacker_state.generate_proposal(
            planner_type=req.planner,
            objective_hint=req.objective_hint,
        )
        return {
            "proposal_id": attacker_state.pending_proposal_id,
            "proposal": proposal.model_dump() if proposal else None,
            "validation": validation.model_dump(),
            "planner_label": planner_label,
            "strategy_rationale": strategy_rationale,
            "observed_telemetry": observed_telemetry.model_dump() if observed_telemetry else None,
            "message": "Candidate proposal generated. Human approval required before execution." if validation.valid else "Proposal was rejected or failed validation.",
        }
    except Exception as e:
        logger.error(f"Proposal generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate attack proposal: {e}",
        )


@app.post("/api/attacker/execute", response_model=AttackFeedback)
def execute_attack():
    """Human-in-the-loop action: Submit the pending validated proposal to Part 1 Attack Gateway."""
    try:
        feedback = attacker_state.execute_pending_proposal()
        return feedback
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except GatewayClientError as e:
        err_msg = str(e)
        if "HTTP 429" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=err_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gateway execution error: {err_msg}",
        )


@app.post("/api/attacker/discard")
def discard_proposal():
    """Discard pending proposal without executing."""
    attacker_state.discard_pending_proposal()
    return {"message": "Pending proposal discarded."}


@app.get("/api/attacker/history")
def get_attack_history():
    """Return list of historical attack proposals and execution outcomes."""
    return [h.model_dump() for h in reversed(attacker_state.history)]


@app.get("/api/attacker/experiments")
def get_experiments():
    """Return immutable log of all executed adversarial evaluation experiments."""
    return [exp.model_dump() for exp in reversed(attacker_state.experiments)]


@app.post("/api/attacker/reset")
def reset_system():
    """Reset Part 1 Attack Gateway and local attacker state."""
    try:
        return attacker_state.reset()
    except GatewayClientError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gateway reset failed: {e}",
        )
