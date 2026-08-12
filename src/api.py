"""
واجهة REST API لمحاكاة النظام التناظري.

تشغيل الخادم:
    uvicorn src.api:app --reload

التوثيق التفاعلي:
    http://127.0.0.1:8000/docs
"""

from __future__ import annotations

from dataclasses import asdict

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .analog_simulation import (
    AnalogSimulationConfig,
    TrialResult,
    run_simulation,
)


app = FastAPI(
    title="Continuous Analog Simulation API",
    description=(
        "واجهة للتحكم في محاكاة طرح القنوات التناظرية "
        "وتقدير التأخير باستخدام أقل طاقة للفرق."
    ),
    version="1.0.0",
)


class SimulationRequest(BaseModel):
    """الإعدادات التي يمكن تعديلها من خلال API."""

    duration_seconds: float = Field(
        default=0.004,
        gt=0.0,
    )

    numerical_points: int = Field(
        default=40_000,
        ge=100,
        le=500_000,
    )

    min_true_delay_seconds: float = Field(
        default=5.0e-6,
        ge=0.0,
    )

    max_true_delay_seconds: float = Field(
        default=20.0e-6,
        gt=0.0,
    )

    min_search_delay_seconds: float = Field(
        default=0.0,
        ge=0.0,
    )

    max_search_delay_seconds: float = Field(
        default=30.0e-6,
        gt=0.0,
    )

    search_points: int = Field(
        default=601,
        ge=3,
        le=10_001,
    )

    trials: int = Field(
        default=10,
        ge=1,
        le=1_000,
    )

    channel_1_gain: float = Field(
        default=1.0,
        gt=0.0,
    )

    channel_2_gain: float = Field(
        default=0.99,
        gt=0.0,
    )

    channel_1_noise_std: float = Field(
        default=0.001,
        ge=0.0,
    )

    channel_2_noise_std: float = Field(
        default=0.001,
        ge=0.0,
    )

    fit_gain: bool = True

    refine_minimum: bool = True

    random_seed: int = 42


class TrialResponse(BaseModel):
    """نتيجة تجربة واحدة."""

    trial_index: int
    true_delay_seconds: float
    estimated_delay_seconds: float
    timing_error_seconds: float
    timing_error_microseconds: float
    distance_error_millimeters: float
    minimum_energy: float
    refined_energy: float | None


class SummaryResponse(BaseModel):
    """ملخص النتائج."""

    mean_absolute_timing_error_us: float
    median_absolute_timing_error_us: float
    mean_distance_error_mm: float
    median_distance_error_mm: float
    percentile_90_distance_error_mm: float
    maximum_distance_error_mm: float


class SimulationResponse(BaseModel):
    """الاستجابة الكاملة للمحاكاة."""

    configuration: SimulationRequest
    summary: SummaryResponse
    trials: list[TrialResponse]


@app.get("/")
def root() -> dict[str, str]:
    """اختبار أن الخدمة تعمل."""
    return {
        "service": "Continuous Analog Simulation API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """فحص حالة الخادم."""
    return {"status": "ok"}


def build_simulation_config(
    request: SimulationRequest,
) -> AnalogSimulationConfig:
    """تحويل طلب API إلى إعدادات المحاكاة."""
    return AnalogSimulationConfig(
        duration_seconds=request.duration_seconds,
        numerical_points=request.numerical_points,
        min_true_delay_seconds=(
            request.min_true_delay_seconds
        ),
        max_true_delay_seconds=(
            request.max_true_delay_seconds
        ),
        min_search_delay_seconds=(
            request.min_search_delay_seconds
        ),
        max_search_delay_seconds=(
            request.max_search_delay_seconds
        ),
        search_points=request.search_points,
        trials=request.trials,
        channel_1_gain=request.channel_1_gain,
        channel_2_gain=request.channel_2_gain,
        channel_1_noise_std=(
            request.channel_1_noise_std
        ),
        channel_2_noise_std=(
            request.channel_2_noise_std
        ),
        fit_gain=request.fit_gain,
        refine_minimum=request.refine_minimum,
        random_seed=request.random_seed,
    )


def create_summary(
    results: list[TrialResult],
) -> SummaryResponse:
    """حساب ملخص إحصائي للنتائج."""
    timing_errors_us = np.array(
        [
            result.timing_error_microseconds
            for result in results
        ],
        dtype=np.float64,
    )

    distance_errors_mm = np.array(
        [
            result.distance_error_millimeters
            for result in results
        ],
        dtype=np.float64,
    )

    return SummaryResponse(
        mean_absolute_timing_error_us=float(
            np.mean(np.abs(timing_errors_us))
        ),
        median_absolute_timing_error_us=float(
            np.median(np.abs(timing_errors_us))
        ),
        mean_distance_error_mm=float(
            np.mean(distance_errors_mm)
        ),
        median_distance_error_mm=float(
            np.median(distance_errors_mm)
        ),
        percentile_90_distance_error_mm=float(
            np.percentile(distance_errors_mm, 90)
        ),
        maximum_distance_error_mm=float(
            np.max(distance_errors_mm)
        ),
    )


@app.post(
    "/simulate",
    response_model=SimulationResponse,
)
def simulate(
    request: SimulationRequest,
) -> SimulationResponse:
    """تشغيل المحاكاة بالإعدادات المرسلة."""
    try:
        config = build_simulation_config(request)
        results = run_simulation(config)
        summary = create_summary(results)

        trial_responses = [
            TrialResponse(
                **asdict(result)
            )
            for result in results
        ]

        return SimulationResponse(
            configuration=request,
            summary=summary,
            trials=trial_responses,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "حدث خطأ أثناء تشغيل المحاكاة: "
                f"{error}"
            ),
        ) from error