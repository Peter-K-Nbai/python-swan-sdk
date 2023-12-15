""" Tests for Computing Providers """

import pytest
import requests
from mock.mock import Mock, MagicMock, patch
from src.api.cp import get_all_cp_machines, get_cp_detail
from src.constants.constants import SWAN_API
from src.exceptions.request_exceptions import SwanHTTPError, SwanRequestError


class TestComputingProviders:
    def test_retrieve_all_cp_machines(self):
        # Mock the requests.get method to return a mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "hardware": [
                    {"name": "Machine 1", "cpu": "Intel i7", "ram": "16GB"},
                    {"name": "Machine 2", "cpu": "AMD Ryzen 5", "ram": "8GB"},
                    {"name": "Machine 3", "cpu": "Intel i5", "ram": "12GB"},
                ]
            },
        }
        mock_response.raise_for_status.return_value = None
        requests.get = MagicMock(return_value=mock_response)

        # Call the function under test
        result = get_all_cp_machines()

        # Assert that the result is the expected list of hardware configurations
        expected_result = [
            {"name": "Machine 1", "cpu": "Intel i7", "ram": "16GB"},
            {"name": "Machine 2", "cpu": "AMD Ryzen 5", "ram": "8GB"},
            {"name": "Machine 3", "cpu": "Intel i5", "ram": "12GB"},
        ]
        assert result == expected_result

    def test_function_raises_httperror_if_api_call_fails(self):
        # Mock the requests.get method to raise an exception
        with patch("requests.get", side_effect=requests.exceptions.HTTPError):
            with pytest.raises(SwanHTTPError):
                get_all_cp_machines()

    def test_failed_api_response(self):
        # Mock the requests.get method to raise an exception
        with patch("requests.get", side_effect=requests.exceptions.RequestException):
            with pytest.raises(SwanRequestError):
                get_all_cp_machines()

    def test_retrieve_valid_cp_detail(self):
        # Mock the requests.get method to return a mock response
        mock_response = Mock()
        mock_response.json.return_value = {"cp_id": "123", "name": "Test CP"}
        mock_response.status_code = 200
        with patch("requests.get", return_value=mock_response) as mock_get:
            # Call the function with a valid cp_id
            cp_id = "123"
            response, status_code = get_cp_detail(cp_id)

            # Assert that the requests.get method was called with the correct URL
            mock_get.assert_called_once_with(f"{SWAN_API}/{cp_id}")

            # Assert that the response data and status code are correct
            assert response == {"cp_id": "123", "name": "Test CP"}
            assert status_code == 200

    def test_returned_dictionary_contains_expected_keys(self):
        # Mock the requests.get method to return a mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }
        mock_response.status_code = 200
        requests.get = MagicMock(return_value=mock_response)

        # Call the function you're testing
        response, status_code = get_cp_detail("cp_id")

        # Assert that the response contains all expected keys
        assert "key1" in response
        assert "key2" in response
        assert "key3" in response

    def test_http_status_code_type(self):
        # Mock the requests.get method to return a mock response
        mock_response = Mock()
        mock_response.json.return_value = {"data": "mock_data"}
        mock_response.status_code = 200
        with patch("requests.get", return_value=mock_response):
            # Call the function under test
            response, status_code = get_cp_detail("cp_id")

            # Assert that the status code is of the expected type
            assert isinstance(status_code, int)
