# export_results.py
import pandas as pd

def export_to_excel(data, file_name='quiz_results.xlsx'):
    """
    Exports the provided data to an Excel file.
    
    Args:
    - data (list of dict): List containing dictionaries of quiz results.
    - file_name (str): The name of the Excel file.
    """
    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False)
    print(f"Results successfully exported to {file_name}")
