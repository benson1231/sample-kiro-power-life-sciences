"""DICOM query client.

Provides DICOM query/retrieve interface.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "DICOM"
BASE_URL = "https://dicomweb.example.org/dicom-web/"


async def query(
    server: BaseLifeSciencesServer,
    patient_id: str = "",
    modality: str = "",
) -> dict[str, Any]:
    """Query DICOM studies by patient ID and/or modality."""
    url = f"{BASE_URL}studies"
    params: dict[str, Any] = {}
    if patient_id:
        params["PatientID"] = patient_id
    if modality:
        params["ModalitiesInStudy"] = modality
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=patient_id or modality)
    return response.json()
