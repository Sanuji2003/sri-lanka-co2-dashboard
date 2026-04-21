import pandas as pd

# STEP 1: Load the raw CSV file
# pd.read_csv reads your spreadsheet into Python as a table
df = pd.read_csv("lka_co2e_20yr_source.csv")

print("Original shape:", df.shape)
# df.shape shows (number of rows, number of columns)
# You should see: (3384, 18)

# STEP 2: Remove rows where emissions are zero
# These rows have no useful information for our charts
df = df[df["emissionsQuantity"] > 0].copy()
print("After removing zeros:", df.shape)

# STEP 3: Remove 2026 data - it is incomplete (only ~9% of a year)
# Including 2026 would falsely show a 91% drop in emissions
# which would mislead decision-makers - the opposite of good data science
df = df[df["year"].astype(str) != "2026"].copy()
print("After removing 2026:", df.shape)

# STEP 4: Keep only the columns we actually need
columns_to_keep = [
    "name",              # location name e.g. Colombo Division
    "sector",            # broad category e.g. transportation
    "subsector",         # specific e.g. road-transportation
    "sourceType",        # gadm-aggregation or point-source
    "emissionsQuantity", # main value: tonnes of CO2
    "activity",          # energy used
    "capacity",          # size of facility
    "year",              # 2024 or 2025 only
]

df = df[columns_to_keep].copy()
print("Columns after cleaning:", df.columns.tolist())

# STEP 5: Convert year from text to a number
# '2024' (text) becomes 2024 (number) so Python sorts correctly
df["year"] = df["year"].astype(int)

# STEP 6: Add a new column - emissions in MILLIONS of tonnes
# Raw numbers are huge (e.g. 9,863,554 tonnes)
# Dividing by 1 million gives 9.86 which is easier to read on charts
df["emissions_mt"] = df["emissionsQuantity"] / 1_000_000

# STEP 7: Check for any missing values
# isnull().sum() counts empty cells in each column
# All should be zero after our cleaning
print("\nMissing values per column:")
print(df.isnull().sum())

# STEP 8: Print a summary
print("\nSectors:", df["sector"].unique())
print("Years remaining:", sorted(df["year"].unique()))
print("Total rows in clean data:", len(df))

# STEP 9: Save the clean data to a new file
# index=False means do not add an extra number column
try:
    df.to_csv("clean_data.csv", index=False)
    print("\nSuccess! clean_data.csv saved.")
except PermissionError as exc:
    raise SystemExit(
        "\nCould not save clean_data.csv. Close the file in Excel or any other app, "
        "then run clean_data.py again."
    ) from exc
