# Reddit Summary Generator

** warning potentially expensive, be careful **

This script is used to generate summaries of Reddit threads by using the OpenAI API to complete chunks of text based on a prompt. It starts by making a request to a specified Reddit thread, extracting the title and self text, and then finding all of the comments in the thread. These comments are then concatenated into groups of a specified number of tokens, and a summary is generated for each group by prompting the OpenAI API with the group's text and the title and self text of the Reddit thread. The summaries are then saved to a file in an `outputs` folder in the current working directory.

## Requirements

-   Python 3
-   openai (`pip install openai`)
-   jsonpath-ng (`pip install jsonpath-ng`)
-   requests (`pip install requests`)
-   dotenv (`pip install python-dotenv`)

## Usage

1.  Obtain an OpenAI API key and set it as an environment variable with the name `OPENAI_API_KEY`.
2.  Run the script with `python reddit.py`.
3.  The summary will be saved to a file in the `outputs` folder in the current working directory.

## Configuration

The following variables at the top of the script can be modified to change the behavior of the script:

-   `CHUNK_SIZE`: The maximum number of tokens to include in each group that a summary is generated for.
-   `GROUP_LIMIT`: The maximum number of groups to generate summaries for.

## Notes

-   The script uses the `text-davinci-003` model to generate summaries.
-   The script relies on the `jsonpath-ng` library to extract data from the Reddit thread's JSON response. More information about this library and how to use it can be found [here](https://jsonpath-ng.readthedocs.io/en/latest/).
-   The script uses the `dotenv` library to load environment variables from a `.env` file. More information about this library and how to use it can be found [here](https://pypi.org/project/python-dotenv/).