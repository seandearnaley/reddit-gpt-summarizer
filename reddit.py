# Import necessary modules
from datetime import datetime
import openai
import os
from jsonpath_ng.ext import parse
import re
import json
import requests
from bs4 import BeautifulSoup
from transformers import GPT2Tokenizer
from dotenv import load_dotenv

load_dotenv()

# Set up the tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Headers to mimic a browser visit
headers = {'User-Agent': 'Mozilla/5.0'}

# number of tokens to summarize to
CHUNK_SIZE = 1600

openai.organization = os.environ.get("OPENAI_ORG_ID")
openai.api_key = os.environ.get("OPENAI_API_KEY")


def complete_chunk(prompt, tokenizer):
    tokens = tokenizer.tokenize(prompt)
    # print('prompt=' + prompt)
    token_length = len(tokens)

    print('token length: ' + str(token_length))
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=4000-token_length,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6
    )
    # print(response)
    # print(response.choices[0].text)
    return response.choices[0].text


def concatenate_bodies(contents, tokenizer):
    # Concatenate the bodies into an array of CHUNK_SIZE token strings
    results = []
    result = ""
    for t in contents:
        if t[1].strip():
            t = (t[0], re.sub(r"\n+", "\n", t[1]))
            result += t[1].strip() + "\n"
            tokens = tokenizer.tokenize(result)
            token_length = len(tokens)
            if token_length > CHUNK_SIZE:
                results.append(result)
                result = ""
    if result:
        results.append(result)
    return results


# def get_body_contents(data, path=[]):
#     results = []
#     if isinstance(data, dict):
#         for key, value in data.items():
#             if key == 'body':
#                 path_str = '/'.join([str(x) for x in path])
#                 results.append((path_str, value))
#             else:
#                 results.extend(get_body_contents(value, path + [key]))
#     elif isinstance(data, list):
#         for index, item in enumerate(data):
#             results.extend(get_body_contents(item, path + [index]))
#     return results


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


def download_parse_reddit_thread(url):
    # Make a request to the URL and retrieve the HTML content
    response = requests.get(url, headers=headers)
    html_content = response.text

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(html_content, 'html.parser')

    return soup.get_text("|", strip=True).replace("Reply|Share|Report|Save|Follow", "")


# Make a request to the URL and retrieve the JSON content IMPORTANT: make sure it's json
response = requests.get(
    'https://www.reddit.com/r/StableDiffusion/comments/xr5hgl/fastdreambooth_colab_65_speed_increase_less_than.json', headers=headers)

data = response.json()

# Create a JSONPath expression to find the first item with a "title" attribute
title = parse('$..title').find(data)[0].value

# initialize the prefix with the title of the reddit thread
prefix = f"Title: {title}"

contents = list(get_body_contents(data, []))
print(contents, "\n\nlength=", len(contents))

groups = concatenate_bodies(contents, tokenizer)

# Get the current working directory
cwd = os.getcwd()

# Define the relative path to the output folder
output_folder = 'outputs'

# Construct the full path to the output folder
output_path = os.path.join(cwd, output_folder)

# Create the output folder if it does not exist
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Create the output filename with a timestamp
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
output_filename = f'output_{timestamp}.txt'

# Construct the full path to the output file
output_file_path = os.path.join(output_path, output_filename)

output = "START\n\n"
i = 0
for group in groups[:2]:
    prompt = f"{prefix}\n\nTake any addition information provided in this thread and update/enhance the article, revise and punctuate as necessary \n\n BEGIN\n\n{group}\n\nEND"
    summary = complete_chunk(prompt, tokenizer)
    prefix = f"Title: {title}\n\n{summary}"
    output += f"\n\n============\nSUMMARY COUNT: " + \
        str(i) + "\n============\n\n"
    output += summary
    i += 1

# Save the output to a file
with open(output_file_path, "w") as f:
    f.write(output)


print(output)
