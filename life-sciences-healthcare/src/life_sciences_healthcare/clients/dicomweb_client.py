"""DICOMweb API client.

Provides DICOMweb QIDO-RS query interface.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "DICOMweb"
BASE_URL = "https://dicomweb.example.org/dicom-web/"


async def query(
    server: BaseLifeSciencesServer,
    patient_id: str = "",
    study_date: str = "",
) -> dict[str, Any]:
    """Query DICOMweb studies by patient ID and/or study date."""
    url = f"{BASE_URL}studies"
    params: dict[str, Any] = {}
    if patient_id:
        params["PatientID"] = patient_id
    if study_date:
        params["StudyDate"] = study_date
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=patient_id or study_date)
    return response.json()
