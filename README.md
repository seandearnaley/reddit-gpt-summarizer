# Reddit GPT Summarizer

## warning potentially expensive, be careful

This script is used to generate summaries of Reddit threads by using the OpenAI API to complete chunks of text based on a prompt. It starts by making a request to a specified Reddit thread, extracting the title and self text, and then finding all of the comments in the thread. These comments are then concatenated into groups of a specified number of tokens, and a summary is generated for each group by prompting the OpenAI API with the group's text and the title and self text of the Reddit thread. The summaries are then saved to a file in an `outputs` folder in the current working directory.

## Requirements

- Python 3.8 or higher
- `openai` module
- `dotenv` module
- API key for OpenAI

## Installation

1. Clone the repository: `git clone https://github.com/[USERNAME]/reddit-summary-generator.git`
2. Navigate to the project directory: `cd reddit-summary-generator`
3. Install the necessary modules: `pip install -r requirements.txt`
4. Create a `.env` file in the root directory and add the following environment variables:
    - `OPENAI_ORG_ID`: your OpenAI organization ID
    - `OPENAI_API_KEY`: your OpenAI API key

## Configuration Parameters

The following parameters can be modified in `main.py` to customize the summary generation process:

- `MAX_CHUNK_SIZE`: the maximum number of tokens that can be included in a single summary chunk.
- `MAX_NUMBER_OF_SUMMARIES`: the maximum number of summaries to generate.
- `MAX_TOKENS`: the maximum number of tokens that can be used in a single OpenAI request.
- `GPT_MODEL`: the OpenAI GPT-3 model to use for generating the summary.
- `INSTRUCTION_TEXT`: the text to provide to the OpenAI model as a prompt.

## Constants

The following constants are used in the script:

- `REDDIT_URL`: the URL of the Reddit thread to summarize.
- `openai.organization`: the OpenAI organization ID.
- `openai.api_key`: the OpenAI API key.

## Notes

- The script uses the `text-davinci-003` model to generate summaries.
- The script uses the `dotenv` library to load environment variables from a `.env` file. More information about this library and how to use it can be found [here](https://pypi.org/project/python-dotenv/).
