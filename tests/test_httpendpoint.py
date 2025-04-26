"""tests/test_httpendpoint.py"""

from unittest.mock import patch, Mock
import requests
from monitor.httpendpoint import HttpEndpoint

def make_endpoint(url="http://localhost", port=80, method="GET", success=200, error=500):
    """
    Создает тестовый экземпляр HttpEndpoint с заданной конфигурацией.
    """
    config = {
        "id": "test",
        "name": "Test Endpoint",
        "url": url,
        "port": port,
        "method": method,
        "success_code": success,
        "error_code": error,
        "interval_main": 300,
        "interval_retry": 10,
        "max_attempts": 3,
    }
    return HttpEndpoint(config)

def test_url_with_port_zero():
    """
    Проверяет, что URL не модифицируется, если port=0.
    """
    endpoint = make_endpoint(port=0)
    assert endpoint.build_full_url() == "http://localhost"

def test_url_with_custom_port():
    """
    Проверяет, что порт корректно добавляется к URL.
    """
    endpoint = make_endpoint(url="http://localhost", port=8080)
    assert endpoint.build_full_url() == "http://localhost:8080"

@patch("monitor.httpendpoint.requests.request")
def test_check_status_success(mock_request):
    """
    Проверяет, что check_status возвращает True при коде 200.
    """
    endpoint = make_endpoint()
    mock_response = Mock(status_code=200)
    mock_request.return_value = mock_response
    ok, code = endpoint.check_status()
    assert ok is True
    assert code == 200

@patch("monitor.httpendpoint.requests.request")
def test_check_status_failure(mock_request):
    """
    Проверяет, что check_status возвращает False при коде 500.
    """
    endpoint = make_endpoint()
    mock_response = Mock(status_code=500)
    mock_request.return_value = mock_response
    ok, code = endpoint.check_status()
    assert ok is False
    assert code == 500

@patch("monitor.httpendpoint.requests.request", \
       side_effect=requests.RequestException("Connection failed"))
def test_check_status_exception(_mock_request):
    """
    Проверяет, что check_status обрабатывает исключения и возвращает код -1.
    """
    endpoint = make_endpoint()
    ok, code = endpoint.check_status()
    assert ok is False
    assert code == -1

@patch("monitor.httpendpoint.requests.request")
def test_check_status_not_found(mock_request):
    """
    Проверяет, что check_status корректно обрабатывает код 404.
    """
    endpoint = make_endpoint()
    mock_response = Mock(status_code=404)
    mock_request.return_value = mock_response

    ok, code = endpoint.check_status()
    assert ok is False
    assert code == 404

@patch("monitor.httpendpoint.requests.request")
def test_check_status_with_post(mock_request):
    """
    Проверяет, что check_status выполняет POST-запрос.
    """
    endpoint = make_endpoint(
        url="http://localhost/healthcheck",
        port=0,
        method="POST"
    )
    mock_response = Mock(status_code=200)
    mock_request.return_value = mock_response

    ok, code = endpoint.check_status()
    assert ok is True
    assert code == 200
    mock_request.assert_called_with(
        "POST", "http://localhost/healthcheck", timeout=5
    )

def test_url_with_embedded_port():
    """
    Проверяет, что порт из URL не затирается дополнительным port-параметром.
    """
    endpoint = make_endpoint(
        url="http://svc2.copytrust.ru:15778/RegistrationService/web/2/healthcheck",
        port=0  # Порт не должен добавляться снова
    )
    assert endpoint.build_full_url() == \
        "http://svc2.copytrust.ru:15778/RegistrationService/web/2/healthcheck"
