from unittest.mock import Mock
from unittest.mock import patch

import pytest

from fastapi import HTTPException

from app.services import measurement_raw_service


def test_get_measurement_by_id_returns_measurement():

    fake_measurement = Mock()

    with patch(
        "app.services.measurement_raw_service.measurement_raw_repository.get_by_id",
        return_value=fake_measurement,
    ):
        result = measurement_raw_service.get_measurement_by_id(
            db=Mock(),
            measurement_id=1,
        )

    assert result == fake_measurement


def test_get_measurement_by_id_not_found():

    with patch(
        "app.services.measurement_raw_service.measurement_raw_repository.get_by_id",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc:
            measurement_raw_service.get_measurement_by_id(
                db=Mock(),
                measurement_id=999,
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Measurement RAW not found"
