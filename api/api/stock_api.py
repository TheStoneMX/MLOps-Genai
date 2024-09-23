
import logging
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import NoReturn

import polars as pl
from fastapi import HTTPException, Query
from fastapi.responses import HTMLResponse

from .data_preparation import prepare_data

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get the path to the project root
project_root = Path(__file__).resolve().parent.parent.parent

@lru_cache(maxsize=1)
def load_data() -> pl.DataFrame:
    """Load and prepare stock data from a CSV file."""
    try:
        file_path = project_root / "data" / "all_stocks_5yr.csv"
        logger.info("Attempting to load data from %s", file_path)
        prepared_df = prepare_data(file_path)
        logger.info("Data loaded successfully")
        return prepared_df
    except Exception as e:
        logger.exception("Error loading data")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while loading data."
        ) from e

def raise_http_exception(status_code: int, detail: str) -> NoReturn:
    """Raise an HTTPException with the given status code and detail."""
    logger.error(detail)
    raise HTTPException(status_code=status_code, detail=detail)

async def calculate_gains(
    name: str = Query(..., description="Company identifier"),
    starting_date: str = Query(..., description="Starting date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    investment: float = Query(..., gt=0, description="Amount invested at starting date"),
) -> HTMLResponse:
    """Calculate gains from stock investments over a specified date range.

        This function calculates the gains from a stock investment based on the specified
        company, date range, and initial investment amount. It raises appropriate errors for
        invalid inputs and returns an HTML response summarizing the results.

    Parameters
    ----------
        - name (str): Company identifier for which gains are to be calculated.
        - starting_date (str): The starting date for the calculation (YYYY-MM-DD).
        - end_date (str): The end date for the calculation (YYYY-MM-DD).
        - investment (float): The amount invested at the starting date (must be greater than 0).

    Returns
    -------
        - HTMLResponse: An HTML response containing the stock gains analysis.

    Raises
    ------
        - HTTPException: If the input is invalid or if no data is found for the specified dates.

    """
    try:
        logger.info(
            "Calculating gains for %s from %s to %s with investment %s",
            name, starting_date, end_date, investment,
        )
        
        # Validate input dates
        try:
            start_date = datetime.strptime(starting_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as ve:
            raise_http_exception(400, f"Invalid date format. Use YYYY-MM-DD. Error: {ve}")

        if start_date >= end_date:
            raise_http_exception(400, "Start date must be before end date.")
        
        # Load the data
        prepared_df = load_data()

        # Filter data for the specified company and date range
        company_data = prepared_df.filter(
            (pl.col("Name") == name) & (pl.col("date") >= start_date) & (pl.col("date") <= end_date)
        )

        if company_data.is_empty():
            raise_http_exception(404, "No data found for the specified company and date range.")

        # Get the opening price on the starting date and closing price on the end date
        start_price_data = company_data.filter(pl.col("date") == start_date)
        end_price_data = company_data.filter(pl.col("date") == end_date)

        if start_price_data.is_empty() or end_price_data.is_empty():
            raise_http_exception(404, "No data found for the specified dates.")

        start_price = start_price_data["open"].item()
        end_price = end_price_data["close"].item()


        # Calculate gains
        # Gains are computed the following way: (close in end_date / open in starting_date) * investment
        gains = (end_price / start_price) * investment
        
        percent_change = ((end_price - start_price) / start_price) * 100
        
        logger.info("Calculation successful. Gains: %s", gains)

        # Format the response as HTML
        html_content = f"""
        <html>
            <head>
                <title>Stock Gains Analysis</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
                    h1 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .positive {{ color: green; }}
                    .negative {{ color: red; }}
                </style>
            </head>
            <body>
                <h1>Stock Gains Analysis</h1>
                <table>
                    <tr><th>Company</th><td>{name}</td></tr>
                    <tr><th>Starting Date</th><td>{starting_date}</td></tr>
                    <tr><th>End Date</th><td>{end_date}</td></tr>
                    <tr><th>Initial Investment</th><td>${investment:,.2f}</td></tr>
                    <tr><th>Starting Price</th><td>${start_price:.2f}</td></tr>
                    <tr><th>Ending Price</th><td>${end_price:.2f}</td></tr>
                    <tr><th>Gains/Losses</th><td class="{'positive' if gains >= 0 
                    else 'negative'}">${gains:,.2f}</td></tr>
                    <tr><th>Percent Change</th><td class="{'positive' if percent_change >= 0 
                    else 'negative'}">{percent_change:.2f}%</td></tr>
                    <tr><th>Final Value</th><td>${(investment + gains):,.2f}</td></tr>
                </table>
            </body>
        </html>
        """

        return HTMLResponse(content=html_content, status_code=200)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in calculate_gains")
        raise HTTPException(
        status_code=500,
        detail="Internal server error while calculating gains"
    ) from e
    
