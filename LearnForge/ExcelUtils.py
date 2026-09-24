import pandas as pd

def readExcel(file_path, sheet_name):
    """
    Reads data from an Excel file and returns it as a pandas DataFrame.

    :param file_path: Path to the Excel file.
    :param sheet_name: Name of the sheet to read.
    :return: List of dictionaries containing the data.
    """

    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    return df
