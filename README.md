# Reddit GPT Summarizer

## warning potentially expensive, be careful

A python project that uses OpenAI's GPT-3 model to generate a summary of a Reddit thread based on its comments. The project is built using poetry and makes use of various other tools like dotenv and tiktoken.

This script is used to generate summaries of Reddit threads by using the OpenAI API to complete chunks of text based on a prompt with recursive summarization. It starts by making a request to a specified Reddit thread, extracting the title and self text, and then finding all of the comments in the thread. These comments are then concatenated into groups of a specified number of tokens, and a summary is generated for each group by prompting the OpenAI API with the group's text and the title and self text of the Reddit thread. The summaries are then saved to a file in an `outputs` folder in the current working directory.

## Prerequisites

- Python 3.8 or later
- OpenAI API Key
- Poetry

## Installation

1. Clone the repository

`$ git clone https://github.com/<username>/reddit-gpt-summarizer.git`

2. Change into the project directory

`$ cd reddit-gpt-summarizer`

3. Create a virtual environment

`$ poetry shell`

4. Install the dependencies

`$ poetry install`

5. Create a `.env` file in the project root directory and add the following environment variables:

`OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
`OPENAI_ORG_ID=<YOUR_OPENAI_ORG_ID>`

## Usage

1. Run the `main.py` script

`$ python reddit_gpt_summarizer/main.py`

The script will take a Reddit URL and use OpenAI's GPT-3 model to generate a summary of the Reddit thread based on its comments. The summary will be displayed in the console and also saved to a file in the `outputs` folder.

## Tests

The project contains tests for the `main.py` and `utils.py` scripts. To run the tests, use the following command:

`$ poetry run pytest`

## Output

The output is saved as a text file in the `outputs` folder with the title of the Reddit thread and a timestamp in the filename.

## Folder Structure

- outputs: folder containing the generated summary files
- reddit_gpt_summarizer: folder containing the main script and the utilities
  - utils: folder containing utility functions
  - main.py: script that uses OpenAI's GPT-3 model to generate a summary of a Reddit thread
  - output.json: raw json output of the Reddit thread for debugging purposes
- tests: folder containing test files
- .env: file containing the environment variables for OpenAI's API key and organization ID
- .gitignore: file specifying files to be ignored by Git
- README.md: file containing documentation for the project
- poetry.lock: file containing poetry's project dependencies and version information
- pyproject.toml: file containing project metadata and dependencies
- requirements.txt: file containing the project's dependencies in pip format
