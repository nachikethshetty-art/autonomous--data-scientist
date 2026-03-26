"""
FastAPI Backend - Data Ingestion Endpoints
Module 19: API Routes
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import json
import numpy as np

# Lazy import - DataValidator will be imported only when needed
# This avoids loading pandas at startup
DataValidator = None


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# Load environment
load_dotenv()

# Global state
validator = None

def _get_validator():
    """Lazy load DataValidator to avoid importing pandas at startup."""
    global DataValidator
    if DataValidator is None:
        from src.ingestion.validator import DataValidator as DV
        DataValidator = DV
    return DataValidator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    global validator
    try:
        # Try to initialize validator (may fail if pandas not available)
        validator_class = _get_validator.__code__.co_consts
        ValidatorClass = __import__('src.ingestion.validator', fromlist=['DataValidator']).DataValidator
        validator = ValidatorClass()
        print("✅ API started - DataValidator initialized")
    except ImportError:
        print("⚠️  DataValidator not available (pandas not installed)")
        validator = None
    yield
    print("🛑 API shutdown")


# Create FastAPI app
app = FastAPI(
    title="Autonomous AI Data Scientist",
    description="AutoML system with multi-agent orchestration",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Autonomous AI Data Scientist",
        "version": "0.1.0",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Autonomous AI Data Scientist API",
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================================
# DATA INGESTION ENDPOINTS (Module 1)
# ============================================================================


@app.post("/api/v1/upload")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload CSV file for analysis.

    Returns:
        - job_id: Unique identifier for this upload
        - schema: Detected data types and statistics
        - validation_results: Data quality checks
        - metadata: Summary statistics
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    try:
        content = await file.read()
        content_str = content.decode("utf-8")

        result = validator.upload_csv(content_str, file.filename)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        # Use FastAPI's jsonable_encoder to handle any remaining numpy types
        encoded_result = jsonable_encoder(result)
        return encoded_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get job status and metadata.

    Args:
        job_id: Job identifier from upload

    Returns:
        Job details with schema, validations, metadata
    """
    try:
        job_data = validator.get_job_status(job_id)

        if "error" in job_data:
            raise HTTPException(status_code=404, detail=job_data["error"])

        return JSONResponse(status_code=200, content=job_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")


@app.get("/api/v1/jobs")
async def list_jobs(limit: int = 10):
    """
    List recent upload jobs.

    Args:
        limit: Number of recent jobs to return

    Returns:
        List of jobs with basic metadata
    """
    try:
        jobs = validator.list_jobs(limit=limit)
        return JSONResponse(status_code=200, content={"jobs": jobs, "count": len(jobs)})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


# ============================================================================
# PLACEHOLDER ENDPOINTS (To be implemented in later modules)
# ============================================================================


@app.post("/api/v1/jobs/{job_id}/detect-problem")
async def detect_problem(job_id: str, business_context: dict = None):
    """
    Module 3: Auto-detect problem type (classification/regression).
    Coming in Week 1.
    """
    return JSONResponse(
        status_code=501,
        content={"message": "Problem detection coming in Week 1", "job_id": job_id},
    )


@app.post("/api/v1/jobs/{job_id}/clean")
async def clean_data(job_id: str):
    """
    Module 5: Clean data with intelligent transformations.
    Coming in Week 2.
    """
    return JSONResponse(
        status_code=501,
        content={"message": "Data cleaning coming in Week 2", "job_id": job_id},
    )


@app.post("/api/v1/jobs/{job_id}/eda")
async def run_eda(job_id: str):
    """
    Module 6: Generate EDA plots and statistics.
    Coming in Week 2.
    """
    return JSONResponse(
        status_code=501,
        content={"message": "EDA generation coming in Week 2", "job_id": job_id},
    )


@app.post("/api/v1/jobs/{job_id}/train")
async def train_models(job_id: str):
    """
    Module 8: Train AutoML models with Optuna.
    Coming in Week 2.
    """
    return JSONResponse(
        status_code=501,
        content={"message": "Model training coming in Week 2", "job_id": job_id},
    )


@app.get("/api/v1/jobs/{job_id}/results")
async def get_results(job_id: str):
    """
    Module 9-10: Get evaluation, SHAP, and insights.
    Coming in Week 3.
    """
    return JSONResponse(
        status_code=501,
        content={"message": "Results coming in Week 3", "job_id": job_id},
    )


@app.post("/api/v1/jobs/{job_id}/chat")
async def chat_with_data(job_id: str, query: str):
    """
    Module 14: RAG-based chat with your data.
    Coming in Week 3.
    """
    return JSONResponse(
        status_code=501,
        content={
            "message": "Chat interface coming in Week 3",
            "job_id": job_id,
            "query": query,
        },
    )


@app.post("/api/v1/jobs/{job_id}/deploy")
async def deploy_model(job_id: str):
    """
    Module 18: Deploy model and get prediction endpoint.
    Coming in Week 4.
    """
    return JSONResponse(
        status_code=501,
        content={"message": "Model deployment coming in Week 4", "job_id": job_id},
    )


@app.post("/api/v1/predict/{job_id}")
async def predict(job_id: str, data: dict):
    """
    Module 19: Get predictions from deployed model.
    Coming in Week 4.
    """
    return JSONResponse(
        status_code=501,
        content={"message": "Prediction endpoint coming in Week 4", "job_id": job_id},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
    )
