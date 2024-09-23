import polars as pl  # noqa: D100

from alxn_test.processing.subtract_group_mean import subtract_group_mean


def test_subtract_group_mean() -> None:
    """
    Tests the subtract_group_mean function by checking if it correctly subtracts 
    the mean of the grouped column and adds a new column with the group mean.
    """  # noqa: D212
    df = pl.DataFrame({  # noqa: PD901
        "group_col": ["A", "A", "B", "B", "C"],
        "val_col": [10, 20, 30, 40, 50]
    })

    expected_df = pl.DataFrame({
        "group_col": ["A", "A", "B", "B", "C"],
        "val_col_mean_by_group_col": [15.0, 15.0, 35.0, 35.0, 50.0],
        "val_col": [-5.0, 5.0, -5.0, 5.0, 0.0],
    })

    # Apply the function
    result_df = subtract_group_mean(df, "group_col", "val_col")

    # Ensure the column order is the same before comparing
    result_df = result_df.select(["group_col", "val_col_mean_by_group_col", "val_col"])


    # Compare the DataFrames
    assert result_df.equals(expected_df)

