# Import necessary modules
from datetime import datetime
import openai
import os
from jsonpath_ng.ext import parse
import re
import requests
from dotenv import load_dotenv
from utils import get_token_length, generate_filename
from pathlib import Path

load_dotenv()

# number of tokens to summarize to
CHUNK_SIZE = 1600
GROUP_LIMIT = 2

openai.organization = os.environ.get("OPENAI_ORG_ID")
openai.api_key = os.environ.get("OPENAI_API_KEY")


def complete_chunk(prompt) -> str:
    print('prompt=' + prompt)
    print('token length: ' + str(get_token_length(prompt)))
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=4000-get_token_length(prompt),
        # top_p=1,
        # frequency_penalty=0,
        # presence_penalty=0.6
    )
    # print(response)
    # print(response.choices[0].text)
    return response.choices[0].text


def concatenate_bodies(contents):
    # Concatenate the bodies into an array of CHUNK_SIZE token strings
    results = []
    result = ""
    for t in contents:
        if t[1].strip():
            t = (t[0], re.sub(r"\n+", "\n", t[1]))
            result += t[1].strip() + "\n"
            if get_token_length(result) > CHUNK_SIZE:
                results.append(result)
                result = ""
    if result:
        results.append(result)
    return results


def get_body_contents(data, path=[]):
    if isinstance(data, dict):
        if 'body' in data:
            path_str = '/'.join([str(x) for x in path])
            yield (path_str, data['body'])
        for key, value in data.items():
            yield from get_body_contents(value, path + [key])
    elif isinstance(data, list):
        for index, item in enumerate(data):
            yield from get_body_contents(item, path + [index])


def main():
    # Make a request to the URL and retrieve the JSON content
    with requests.get(
            'https://www.reddit.com/r/technology/comments/zairq3/googles_dreambooth_research_has_led_to_a.json', headers={'User-Agent': 'Mozilla/5.0'}) as response:
        data = response.json()

    # Create a JSONPath expression to find the first item with a "title" attribute
    title = parse('$..title').find(data)[0].value
    selftext = parse('$..selftext').find(data)[0].value

    # get an array of body contents
    contents = list(get_body_contents(data, []))

    groups = concatenate_bodies(contents)

    # Get the current working directory
    cwd = os.getcwd()

    # Define the relative path to the output folder
    output_folder = 'outputs'

    # Construct the full path to the output folder
    output_path = os.path.join(cwd, output_folder)

    # Create the output folder if it does not exist
    os.makedirs(output_path, exist_ok=True)

    # Create the output filename with a timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f'{generate_filename(title)}_{timestamp}.txt'

    # initialize the prefix with the title of the reddit thread
    prefix = f"Title: {title}\n{selftext}"

    # Construct the full path to the output file
    output_file_path = os.path.join(output_path, output_filename)

    # Use f-strings for string formatting
    output = f"START\n\n"

    # Use enumerate to get the index and the group in each iteration
    for i, group in enumerate(groups[:GROUP_LIMIT]):
        # Use triple quotes to create a multi-line string
        prompt = f"""{prefix}

Building upon this information, create an article, use any additional relevant information provided in the comment thread below to update/enhance, revise and punctuate.

COMMENTS BEGIN
{group}
COMMENTS END

Title:"""
        summary = complete_chunk(prompt)
        prefix = f"{title}\n\n{summary}\nEND"
        # Use format method to insert values into a string
        output += f"\n\n============\nSUMMARY COUNT: {i}\n============\n\n"
        output += summary

    # Use the Path.write_text method to write to the output file
    Path(output_file_path).write_text(output)

    print(output)


if __name__ == "__main__":
    main()
