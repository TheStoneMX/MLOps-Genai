"""Main API module that is used as entrypoint for deployment."""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse

from .stock_api import calculate_gains

app = FastAPI(title="S&P 500 Stock API")

@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    """Return an informative HTML page about the Stock Prices Gains Analysis API."""
    return """
    <html>
        <head>
            <title>S&P 500 Stock Prices Gains Analysis API</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
                h1 { color: #333; }
                h2 { color: #666; }
                pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Welcome to the S&P 500 Stock Prices Gains Analysis API</h1>
            <p>This API allows you to calculate the gains for a company's stock over a specified period.</p>

            <h2>Available Endpoint:</h2>
            <pre>/ex2/gains</pre>

            <h2>Parameters:</h2>
            <ul>
                <li><strong>name</strong>: Company identifier (e.g., AAPL for Apple Inc.)</li>
                <li><strong>starting_date</strong>: First date to retrieve information from (YYYY-MM-DD)</li>
                <li><strong>end_date</strong>: Last date to provide information from (YYYY-MM-DD)</li>
                <li><strong>investment</strong>: Amount invested at starting date</li>
            </ul>

            <h2>Example Usage:</h2>
            <pre>/ex2/gains?name=AAPL&starting_date=2013-02-08&end_date=2018-02-07&investment=1000</pre>

            <p>For more details, check the <a href="/docs">API documentation</a>.</p>
        </body>
    </html>
    """

@app.get("/ex2/gains", response_class=HTMLResponse)
async def gains(name: str, starting_date: str, end_date: str, investment: float):
    """Calculate gains for a company in a given period."""
    return await calculate_gains(name, starting_date, end_date, investment)
@app.get("/", response_class=PlainTextResponse)
async def root() -> str:  # noqa: F811
    """Return a simple welcome message.

    :return: A simple welcome message.
    """
    return "Welcome to Alexion MLOps Test API!"


@app.get("/ex0")
async def ex0() -> dict[str, str | dict[str, str]]:
    """Explain what needs to be done on exercise 0.

    :return: Message explaining what needs to be done on exercise 0.
    """
    return {
        "ex0": "Download the following datasets and place them in data directory.",
        "datasets": {
            "stocks": "https://www.kaggle.com/datasets/camnugent/sandp500",
            "red_wine": "https://www.kaggle.com/datasets/uciml/red-wine-quality-cortez-et-al-2009",
        },
    }


@app.get("/ex1", response_class=PlainTextResponse)
async def ex1() -> str:
    """Explain what needs to be done on exercise 1.

    :return: Message explaining what needs to be done on exercise 1.
    """
    return (
        "Review the code in alxn_test/processing/subtract_group_mean.py and reimplement the "
        "function as it should be. Focus on readability, efficiency, and Pythonic best practices "
        "(including documentation).\nWrite in the PR used to deliver the test your review and the "
        "reasoning behind the changes you made.\nTest the function in "
        "tests/unit/test_subtract_group_mean.py (you will need to create the file) with pytest."
    )


@app.get("/ex2", response_class=PlainTextResponse)
async def ex2() -> str:
    """Explain what needs to be done on exercise 2.

    :return: Message explaining what needs to be done on exercise 2.
    """
    return (
        "For this exercise, you will implement an API with FastAPI that will allow users to query "
        "information from an S&P 500 stocks dataset. You need to implement 1 endpoint "
        "``/ex2/gains.`` and test it."
    )


@app.get("/ex3", response_class=PlainTextResponse)
async def ex3() -> str:
    """Explain what needs to be done on exercise 3.

    :return: Message explaining what needs to be done on exercise 3.
    """
    return (
        "Add image definition to the Dockerfile Dockerfile.api so that it exposes the API that has "
        "been defined in exercise 2. You will also need to add the necessary commands to Makefile "
        "so that the API is exposed with make docker_api."
    )


@app.get("/ex4", response_class=PlainTextResponse)
async def ex4() -> str:
    """Explain what needs to be done on exercise 4.

    :return: Message explaining what needs to be done on exercise 4.
    """
    return (
        "Finish the implementation of an ML model training pipeline that has a model competition."
    )


@app.get("/ex5", response_class=PlainTextResponse)
async def ex5() -> str:
    """Explain what needs to be done on exercise 5.

    :return: Message explaining what needs to be done on exercise 5.
    """
    return (
        "Explain how would you deploy the training pipeline implemented in exercise 4 and also "
        "serve the model to other applications though an API, using cloud resources."
    )
