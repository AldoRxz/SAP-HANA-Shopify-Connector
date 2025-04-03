import os
import pandas as pd
from dotenv import load_dotenv
from hdbcli import dbapi

# Load environment variables from the .env file
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path, override=True)

# SAP HANA configuration
HANA_CONFIG = {
    'address': os.getenv("HANA_ADDRESS"),
    'port': int(os.getenv("HANA_PORT", 0)),
    'user': os.getenv("HANA_USER"),
    'password': os.getenv("HANA_PASSWORD")
}

# Function to save data to an Excel file
def save_to_excel(df, filename):
    df.to_excel(filename, index=False)

# Function to save data to a JSON file
def save_to_json(df, filename):
    df.to_json(filename, orient="records", lines=True)

# Function to compare data and get the differences
def compare_data(old_df, new_df):
    # Merge the dataframes based on 'ItemCode'
    merged_df = pd.merge(old_df, new_df, on='ItemCode', how='outer', suffixes=('_old', '_new'))
    
    # Check if there were changes in 'OnHand' (stock) or 'Price'
    merged_df['Stock Changed'] = merged_df['OnHand_old'] != merged_df['OnHand_new']
    merged_df['Price Changed'] = merged_df['Price_old'] != merged_df['Price_new']
    
    # Filter only the rows that have changes
    changed_df = merged_df[(merged_df['Stock Changed']) | (merged_df['Price Changed'])]
    
    # Select only the relevant columns
    changed_df = changed_df[['ItemCode', 'Price_old', 'OnHand_old', 'Price_new', 'OnHand_new']]
    
    # Rename the columns for clarity
    changed_df.rename(columns={
        'Price_old': 'Old Price',
        'OnHand_old': 'Old OnHand',
        'Price_new': 'New Price',
        'OnHand_new': 'New OnHand'
    }, inplace=True)
    
    return changed_df

try:
    # Load the old file (productos_iniciales.xlsx)
    old_filename = "productos_iniciales.xlsx"
    if os.path.exists(old_filename):
        old_df = pd.read_excel(old_filename)
    else:
        raise FileNotFoundError(f"The file '{old_filename}' was not found.")
    
    # Connect to SAP HANA and get the new data
    hana_conn = dbapi.connect(**HANA_CONFIG)
    hana_cursor = hana_conn.cursor()
    print("✅ Successfully connected to SAP HANA")

    # SAP HANA query
    hana_query = """
        SELECT  
            O."ItemCode",  
            COALESCE(W."OnHand", 0) AS "OnHand",  
            COALESCE(P."Price", 0) AS "Price"  
        FROM "SBO_MANIJAUTO"."OITM" O
        LEFT JOIN "SBO_MANIJAUTO"."OITW" W 
            ON O."ItemCode" = W."ItemCode" 
            AND W."WhsCode" = 'M'
        LEFT JOIN "SBO_MANIJAUTO"."ITM1" P
            ON O."ItemCode" = P."ItemCode" 
            AND P."PriceList" = 1
        WHERE O."validFor" = 'Y'
        AND O."ItemType" = 'I'
    """
    hana_cursor.execute(hana_query)
    hana_results = hana_cursor.fetchall()
    new_df = pd.DataFrame(hana_results, columns=['ItemCode', 'OnHand', 'Price'])

    # Compare the old data with the new data
    changed_data = compare_data(old_df, new_df)

    # Save the file with only the changes
    if not changed_data.empty:
        output_filename = "productos_diferentes.xlsx"  # Or use ".json" for JSON
        save_to_excel(changed_data, output_filename)  # Save as Excel
        # save_to_json(changed_data, output_filename)  # Or save as JSON
        print(f"✅ A file with the differences has been saved as '{output_filename}'.")
    else:
        print("⚠️ No changes were found in the data.")
    
    # Overwrite the original file with the new data
    save_to_excel(new_df, old_filename)  # Overwrite the file with the new data
    print(f"✅ The file '{old_filename}' has been updated with the latest data.")

    # Close the connections
    hana_cursor.close()
    hana_conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
