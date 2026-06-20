from fastapi import FastAPI, HTTPException, Header
from typing import Optional
from pymongo import MongoClient
from mock_server.models import Session, Testcase, BenchmarkSample
import uuid

app = FastAPI(title="ODE Benchmark API (Mock)")

_benchmarks: dict = {}

SUPPORTED_SOLVERS = {
    "scipy": ["RK45", "RK23", "DOP853", "Radau", "BDF", "LSODA"],
    "eppeer": ["EPP3f4", "EPP4y3", "EPP5f3", "EPP6j1", "EPP7f4", "EPP8d", "EPP9f2"],
    "hairer": ["dopri5", "rk4", "rk45"],
    "boost_odeint": ["rk4", "rk45", "dopri5"],
    "matlab": ["ode45", "ode23", "ode23s", "ode113", "ode15s", "ode23tb"],
    "ubt_ai2_rk": ["seq_A", "seq_E", "seq_F", "seq_PipeD",
                "pthreads_A", "pthreads_E", "pthreads_F", "pthreads_PipeD", "pthreads_AEblock",
                "mpi_A", "mpi_E", "mpi_AEblock"],
}

SUPPORTED_PROBLEMS = [
    "arenstorf", "bruss", "bruss2h", "brussode",
    "hires", "e5", "mbod4h", "vdpol", "cusp", "ks"
]

def get_logs_collection():
    client = MongoClient("mongodb://root:test1234@127.0.0.1:27017/")
    return client["autotest"]["benchmark_logs"]


def _require_token(token: Optional[str]) -> None:
    if token != "test-token-123":
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/api/v1/auth/login")
def login(username: str, password: str):
    if username == "admin" and password == "admin123":
        return {"error_code": "0000", "message": "Login successful", "token": "test-token-123"}
    return {"error_code": "4001", "message": "Invalid credentials"}


@app.get("/api/v1/solvers")
def list_solvers(token: Optional[str] = Header(None)):
    _require_token(token)
    return {"error_code": "0000", "solvers": SUPPORTED_SOLVERS}


@app.get("/api/v1/problems")
def list_problems(token: Optional[str] = Header(None)):
    _require_token(token)
    return {"error_code": "0000", "problems": SUPPORTED_PROBLEMS}


@app.post("/api/v1/benchmark/submit")
def submit_benchmark(library: str, problem: str, solver: str,
                     tolerance: float, thread_count: int = 1,
                     token: Optional[str] = Header(None)):
    _require_token(token)
    if library not in SUPPORTED_SOLVERS:
        raise HTTPException(status_code=400, detail=f"Unsupported library: {library}")
    if solver not in SUPPORTED_SOLVERS[library]:
        raise HTTPException(status_code=400, detail=f"Solver {solver} not available in {library}")
    if problem not in SUPPORTED_PROBLEMS:
        raise HTTPException(status_code=400, detail=f"Unsupported problem: {problem}")
    if tolerance <= 0:
        raise HTTPException(status_code=400, detail="Tolerance must be positive")

    benchmark_id = str(uuid.uuid4())
    _benchmarks[benchmark_id] = {
        "benchmark_id": benchmark_id,
        "library": library,
        "problem": problem,
        "solver": solver,
        "tolerance": tolerance,
        "thread_count": thread_count,
        "status": "completed",
        "error": tolerance * 1.5,
        "execution_time_ms": round(100 / thread_count, 2),
    }
    get_logs_collection().insert_one({
        "benchmark_id": benchmark_id,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        "library": library,
        "problem": problem,
        "solver": solver,
        "tolerance": tolerance,
        "thread_count": thread_count,
        "samples": [
            {"thread_count": i, "error": tolerance * 1.5, "time_ms": round(100 / i, 2)}
            for i in range(1, thread_count + 1)
        ]
    })

    return {"error_code": "0000", "message": "Benchmark submitted", "benchmark_id": benchmark_id}


@app.get("/api/v1/benchmark/{benchmark_id}/status")
def get_benchmark_status(benchmark_id: str, token: Optional[str] = Header(None)):
    _require_token(token)
    if benchmark_id not in _benchmarks:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    bm = _benchmarks[benchmark_id]
    return {"error_code": "0000", "benchmark_id": benchmark_id, "status": bm["status"]}


@app.get("/api/v1/benchmark/{benchmark_id}/results")
def get_benchmark_results(benchmark_id: str, token: Optional[str] = Header(None)):
    _require_token(token)
    if benchmark_id not in _benchmarks:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    return {"error_code": "0000", **_benchmarks[benchmark_id]}

@app.get("/api/v1/benchmark/{benchmark_id}/logs")
def get_benchmark_logs(benchmark_id: str, token: Optional[str] = Header(None)):
    _require_token(token)
    log = get_logs_collection().find_one({"benchmark_id": benchmark_id}, {"_id": 0})
    if not log:
        raise HTTPException(status_code=404, detail="Logs not found")
    return {"error_code": "0000", **log}