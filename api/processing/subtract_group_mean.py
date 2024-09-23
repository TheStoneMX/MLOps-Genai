"""Function to subtract the mean of each group for a given column to each of the rows of said
column."""

import polars as pl
from polars import DataFrame


def subtract_group_mean(df: DataFrame, group_col: str, val_col: str) -> DataFrame:  # noqa: D417
    """Polars offers significant advantages in terms of performance, efficiency,
    and modern data processing features. 
    Its ability to handle large datasets efficiently and execute operations 
    in parallel makes it a strong choice for data-intensive applications.

    We can greatly simplify the original function by eliminating the loops and using built-in 
    polars methods like groupby and transform to handle group operations more efficiently.

    Subtracts the mean of each group for a given column from each row of that column.
    Adds a new column with the mean of each group.

    Parameters
    ----------
        df (pl.DataFrame): The Polars DataFrame containing the data.
        group_col (str): The column name to group by.
        val_col (str): The column name whose group mean is to be subtracted.

    Returns:
    -------
        pl.DataFrame: The DataFrame with the adjusted values and the group mean column.
    """  # noqa: D413, D406, D202

    mean_col = f"{val_col}_mean_by_{group_col}"

    # Use group_by (instead of groupby) to compute group means
    group_means = df.group_by(group_col).agg( pl.col(val_col).mean().alias(mean_col) )

    # Join the group means to the original DataFrame
    df_with_means = df.join(group_means, on=group_col)

    # Subtract the group mean from the original value column
    return df_with_means.with_columns( (pl.col(val_col) - pl.col(mean_col)).alias(val_col) )

