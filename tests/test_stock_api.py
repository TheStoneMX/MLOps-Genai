

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from alxn_test.api import app

client = TestClient(app)


def extract_data_from_html(html_content: str) -> dict[str, str]:
    """Extract data from HTML content into a dictionary."""
    soup = BeautifulSoup(html_content, "html.parser")
    data = {}
    for row in soup.find_all("tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            key = th.text.strip()
            value = td.text.strip()
            data[key] = value
    return data


def test_calculate_gains_valid_input() -> None:
    """Test calculation of gains with valid input."""
    response = client.get("/ex2/gains?name=AAPL&starting_date=2013-02-08&end_date=2018-02-07&investment=1000")
    assert response.status_code == 200
    data = extract_data_from_html(response.text)
    assert all(key in data for key in ["Company", "Starting Date", "End Date", "Initial Investment", "Gains/Losses"])


def test_calculate_gains_invalid_date_format() -> None:
    """Test calculation of gains with invalid date format."""
    response = client.get("/ex2/gains?name=AAPL&starting_date=2013-02-08&end_date=invalid_date&investment=1000")
    assert response.status_code == 400
    assert "Invalid date format" in response.text


def test_calculate_gains_end_date_before_start_date() -> None:
    """Test calculation of gains with end date before start date."""
    response = client.get("/ex2/gains?name=AAPL&starting_date=2018-02-07&end_date=2013-02-08&investment=1000")
    assert response.status_code == 400
    assert "Start date must be before end date" in response.text


def test_calculate_gains_invalid_company() -> None:
    """Test calculation of gains with invalid company."""
    response = client.get("/ex2/gains?name=INVALID&starting_date=2013-02-08&end_date=2018-02-07&investment=1000")
    assert response.status_code == 404
    assert "No data found for the specified company and date range" in response.text


def test_calculate_gains_invalid_date_range() -> None:
    """Test calculation of gains with invalid date range."""
    response = client.get("/ex2/gains?name=AAPL&starting_date=2000-01-01&end_date=2000-01-02&investment=1000")
    assert response.status_code == 404
    assert "No data found for the specified company and date range" in response.text


@pytest.mark.parametrize("investment", [1000, 5000, 10000])
def test_calculate_gains_different_investments(investment: float) -> None:
    """Test calculation of gains with different investment amounts."""
    response = client.get(f"/ex2/gains?name=AAPL&starting_date=2013-02-08&end_date=2018-02-07&investment={investment}")
    assert response.status_code == 200
    data = extract_data_from_html(response.text)
    assert "Initial Investment" in data
    assert float(data["Initial Investment"].replace("$", "").replace(",", "")) == investment
    assert all(key in data for key in ["Gains/Losses", "Percent Change"])
    
