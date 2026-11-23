# NCBI BioSample Survey Parser

## Project Description

This Python project was developed for BIN601 Advanced
Programming for Bioinformatics at Endicott College.

The program retrieves survey information from NCBI BioSample
records associated with the American Gut Project.

Users provide a text file containing BioSample accession IDs
and select a survey question to extract. The program saves
the results as a filtered CSV file for further analysis.

## Features

- Accepts text files containing any number of BioSample IDs.
- Removes duplicate accession IDs.
- Retrieves BioSample information from NCBI.
- Extracts a user-selected survey question.
- Identifies missing survey responses.
- Exports results to a CSV file.
- Allows users to choose the output filename.
- Reports invalid survey questions.

## Requirements

- Python 3
- requests
- beautifulsoup4
- pandas

Install the required packages:

```bash
python -m pip install requests beautifulsoup4 pandas
```

## How to Run

Open a terminal in the project folder.

To extract age categories:

```bash
python biosample_parser.py examples/example_05.txt --question "age cat"
```

To extract alcohol frequency and choose an output filename:

```bash
python biosample_parser.py examples/example_10.txt --question "alcohol_frequency" --output alcohol_results.csv
```

## Input Files

Each input file must contain one BioSample accession per line.

The `examples` folder includes:

- `example_05.txt` — 5 BioSample IDs
- `example_10.txt` — 10 BioSample IDs
- `example_20.txt` — 20 BioSample IDs

## Output

The program creates a CSV file with two columns:

1. BioSample accession ID
2. Response to the selected survey question

Missing responses are left blank in the CSV.

By default, the output file is named
`biosample_survey_results.csv`.

## Error Handling

The program reports failed HTTP requests and skips records
that could not be retrieved.

If the selected survey question does not exist in the
collected data, the program displays an error and examples
of available fields.

## Data Source

NCBI BioSample:
https://www.ncbi.nlm.nih.gov/biosample/

## Notes

The script requires an internet connection.

Processing larger input files may take longer because
each BioSample is retrieved individually.

The structure of NCBI webpages may change over time.