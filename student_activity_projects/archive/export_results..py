import pandas as pd
import os

# Function to export quiz results to Excel
def export_to_excel(results, file_name='quiz_results.xlsx'):
    # Convert the results to a DataFrame
    df = pd.DataFrame(results)

    # Check if the file already exists
    if not os.path.exists(file_name):
        # If not, create a new Excel file with the results
        df.to_excel(file_name, index=False)
    else:
        # If it exists, append the new results to the existing file
        existing_df = pd.read_excel(file_name)
        df = pd.concat([existing_df, df], ignore_index=True)
        df.to_excel(file_name, index=False)
    
    print(f"Results exported to {file_name}")
