"""
BIN601 Advanced Programming for Bioinformatics
Final Project: NCBI BioSample Survey Parser

Description:
    This program retrieves survey responses from NCBI BioSample
    records using a user-provided text file of accession IDs.

    Users can specify a survey question through the command line.
    The program extracts the corresponding responses and exports
    the results to a CSV file.

Input:
    A .txt file containing one BioSample accession per line.

Output:
    A .csv file containing BioSample accessions and responses
    to the selected survey question.

Required external packages:
    requests, beautifulsoup4, pandas

Example:
    python biosample_parser.py examples/example_05.txt --question "age cat"
"""

import requests
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
import time
import argparse

#Set up command-line arguments
parser = argparse.ArgumentParser(
    description="Extract survey responses from NCBI BioSample records.")

#Ask the user to provide an input filename
parser.add_argument(
    "input_file",
    type=Path,
    help="Path to the input file containing BioSample accessions.")

# Allow users to choose which survey question to extract
parser.add_argument(
    "--question",
    type=str,
    required=True,
    help="Survey question to extract, such as 'age cat'"
)

# Allow the user to choose the output CSV filename
parser.add_argument(
    "--output",
    type=Path,
    default=Path("biosample_survey_results.csv"),
    help="Filename for the exported CSV"
)

#Read the arguments supplied in the terminal
args = parser.parse_args()
# 1. Read BioSample accessions from the input file


# Locate the script folder and use the input path provided by the user
project_folder = Path(__file__).resolve().parent
input_file = args.input_file

# Read the accessions and remove empty lines
with open(input_file, "r", encoding="utf-8") as file:
    sample_ids = [line.strip() for line in file if line.strip()]

# Remove duplicate accessions while preserving their order
selected_ids = list(dict.fromkeys(sample_ids))

print("Total IDs in input file:", len(sample_ids))
print("Unique IDs selected:", len(selected_ids))


# 2. Retrieve and extract NCBI BioSample survey data


url = "https://www.ncbi.nlm.nih.gov/biosample/"

# Store the survey information from all BioSamples
records = []

for current_id in selected_ids:

    print("\nProcessing BioSample:", current_id)

    # Request the BioSample webpage from NCBI
    try:
        response = requests.get(
            url,
            params={"term": current_id},
            timeout=20
        )
        response.raise_for_status()

    except requests.RequestException as error:
        print("Request failed:", current_id, error)
        continue

    # Parse the returned HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Create a dictionary for the current BioSample
    record = {"accession": current_id}

    # Find HTML rows containing survey question-answer pairs
    for row in soup.find_all("tr"):

        question_cell = row.find("th")
        answer_cell = row.find("td")

        if question_cell and answer_cell:

            # Extract the question and its corresponding answer
            question = question_cell.get_text(" ", strip=True)
            answer = answer_cell.get_text(" ", strip=True)

            # Store valid question-answer pairs
            if question and answer:
                record[question] = answer

    # Save records containing extracted information
    if len(record) > 1:
        records.append(record)
        print("Fields collected:", len(record) - 1)

    else:
        print("No survey fields found for:", current_id)

    # Pause between requests to avoid overloading NCBI
    time.sleep(0.4)


# 3. Organize the collected records using pandas


# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(records)

if df.empty:
    raise ValueError("No BioSample records were collected.")

print("\nTotal records collected:", len(df))
print("DataFrame shape:", df.shape)
print("Unique BioSamples:", df["accession"].nunique())



# 4. Select meaningful survey questions


# Keep survey responses rather than administrative metadata
survey_columns = [
    "accession",
    args.question
]

# Identify any requested columns that are missing
missing_columns = [
    column for column in survey_columns
    if column not in df.columns
]

# Check that the selected columns exist
if missing_columns:
    available_questions = [
        column for column in df.columns
        if column != "accession"
    ]

    raise ValueError(
        f"Survey question '{args.question}' was not found.\n"
        f"Examples of available questions: {available_questions[:10]}"
    )

# Create a DataFrame containing the selected survey fields
survey_df = df[survey_columns].copy()

# Check how many samples answered the selected question
answered = survey_df[args.question].notna().sum()

# Count samples with no recorded response
missing = survey_df[args.question].isna().sum()

print("\nSurvey response summary:")
print("Question:", args.question)
print("Responses available:", answered)
print("Responses missing:", missing)

# 5. Validate the final survey dataset

unique_samples = survey_df["accession"].nunique()

# Make sure at least one BioSample was collected
if unique_samples == 0:
    raise ValueError(
        "No Biosample records were collected."
    )

print("\nFinal survey dataset:")
print("Rows and columns:", survey_df.shape)
print("Unique BioSamples:", unique_samples)
print("Survey questions:", len(survey_df.columns) - 1)

# Preview several actual survey responses
print("\nSurvey preview:")
print(survey_df.head().to_string(index=False))

# 6. Export the survey results to CSV


# Save the CSV in the same folder as this Python script
output_file = project_folder / args.output

survey_df.to_csv(
    output_file,
    index=False,
    encoding="utf-8"
)

print("\nCSV saved to:", output_file)


# 7. Reopen and verify the saved CSV

# Confirm pandas can read the exported file
saved_df = pd.read_csv(output_file)

if saved_df.shape != survey_df.shape:
    raise ValueError("Saved CSV dimensions do not match.")

if saved_df["accession"].nunique() != unique_samples:
    raise ValueError("Saved CSV has an unexpected accession count.")

print("\nFinal CSV verification:")
print("CSV shape:", saved_df.shape)
print("Unique BioSamples:", saved_df["accession"].nunique())
print("CSV successfully saved and verified!")