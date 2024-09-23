  
import logging
from pathlib import Path
from typing import NoReturn

import polars as pl
from fastapi import HTTPException
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler

# Configure logging
logging.basicConfig(level=logging.INFO)

def prepare_data(file_path: str) -> pl.DataFrame:
    """Prepare the customer data for analysis. This function performs the following steps:
        
        1. Constructs the absolute path to the CSV file based on the provided `file_path`.
        2. Checks if the file exists, raising a `FileNotFoundError` if it does not.
        3. Loads the dataset from the CSV file into a Polars DataFrame.
        4. Converts the 'date' column to datetime format.
        5. Checks for and logs any missing values in the dataset.
        6. Identifies numeric columns for imputation.
        7. Sorts the DataFrame by stock name and date.
        8. Applies KNN imputation to the numeric columns, grouped by stock name.
        9. Checks and logs any remaining missing values after imputation.
        10. Scales the numeric columns using StandardScaler.
        11. Returns the transformed DataFrame grouped by stock name.
               
    Returns
    -------
        - pl.DataFrame: A Polars DataFrame containing the prepared customer data.
        
    Raises
    ------
        - FileNotFoundError: If the specified file does not exist.
        - HTTPException: If an internal server error occurs during data preparation.

    """  # noqa: D400, D415
    
    # Inner function to raise FileNotFoundError
    def raise_file_not_found_error() -> NoReturn:
            raise FileNotFoundError(f"The file {absolute_file_path} does not exist.")

    try:
        # Get the absolute path of the current file
        current_dir = Path(__file__).resolve().parent

        # Construct the absolute path to the CSV file
        absolute_file_path = Path(current_dir) / file_path

        # Check if the file exists
        if not absolute_file_path.exists():
            raise_file_not_found_error()

        # Load the dataset
        customer_data  = pl.read_csv(absolute_file_path)

        # Convert 'date' column to datetime
        customer_data = customer_data.with_columns(pl.col("date").str.to_datetime("%Y-%m-%d"))

        # Check for missing values
        missing_counts = customer_data.null_count()
        logging.info("Missing value counts:")
        logging.info(missing_counts)

        # Identify numeric columns for imputation
        numeric_columns = ["open", "high", "low", "close", "volume"]

        # Sort the dataframe by date and name
        customer_data = customer_data.sort(["Name", "date"])

        # Perform KNN imputation on numeric columns
        imputer = KNNImputer(n_neighbors=5)

        # Group by stock name and apply imputation
        def impute_group(group: pl.DataFrame)-> pl.DataFrame:
            numeric_data = group.select(numeric_columns).to_numpy()
            imputed_data = imputer.fit_transform(numeric_data)
            imputed_df = pl.DataFrame(imputed_data, schema=numeric_columns)
            return group.with_columns(imputed_df)

        customer_data = customer_data.group_by("Name").map_groups(impute_group)

        # Check for any remaining missing values
        remaining_missing = customer_data.null_count()
        logging.info("\nRemaining missing value counts after imputation:")
        logging.info(remaining_missing)

        # Scale the numeric data
        scaler = StandardScaler()

        # Apply scaling to numeric columns
        def scale_group(group: pl.DataFrame)-> pl.DataFrame:
            numeric_data = group.select(numeric_columns).to_numpy()
            scaled_data = scaler.fit_transform(numeric_data)
            scaled_df = pl.DataFrame(scaled_data, schema=numeric_columns)
            return group.with_columns(scaled_df)

        return customer_data.group_by("Name").map_groups(scale_group)

    except Exception as e:
        # Log the error (you might want to use a proper logging system here)
        logging.exception("Error in data preparation")
        # Raise an HTTPException that can be handled by FastAPI
        raise HTTPException(status_code=500,
                            detail="Internal server error during data preparation") from e




