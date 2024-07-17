#!/usr/bin/env python
# coding: utf-8

import os
import sys, fitz
from bs4 import BeautifulSoup
import re
import json
import argparse
import platform

global cell_id

def get_arguments(argv):
    parser = argparse.ArgumentParser(description='PyBib')
    # Simulation settings
    parser.add_argument('-i', '--input_folder', default="")
    parser.add_argument('-n', '--name', default="")
    parser.add_argument('-g', '--gpt', default=False, action='store_true') # string to the gpt model
    parser.add_argument('-r', '--recursive', default=False, action='store_true')
    args = parser.parse_args(argv)

    return args

# Function to extract title from pdf
def extract_title(html_text):
    soup = BeautifulSoup(html_text, features="html.parser")
    spans = soup.find_all('span',style=True)
    usedFontSize = []
    for span in spans:
        styleTag = span['style']
        fontSize = re.findall("font-size:(\d+)",styleTag)
        usedFontSize.append(int(fontSize[0]))
        
    usedFontSize = sorted(set(usedFontSize))
    title_text = []
    while True and len(usedFontSize)>0:
        max_font = usedFontSize[-1]
        usedFontSize = usedFontSize[:-1]
        title_text = []
        for span in spans:
            #print span['style']
            styleTag = span['style']
            fontSize = re.findall("font-size:(\d+)",styleTag)
            if int(fontSize[0]) == max_font:
                title_text.append(span.text)
        if((len(title_text[0]) < 10 or 'arXiv' in title_text[0]) and len(usedFontSize)>0): # Less than 10 letters, more likely to be journal name
            max_font = usedFontSize[-1]
        else:
            break
    
    return ''.join(title_text).strip()


def extract_cell(local_link, model = None, prefix = ""):
    global cell_id
    cells = []
    doc = fitz.open(local_link)
    html_text = ''
    count = 0
    for page in doc:
        html_text += page.get_text('html')
        count += 1
        if(count > 20): #Only extract the first 20 pages
            break
    title = extract_title(html_text)
    
    
    # post process
    title = title.replace("Transportation Research Part E", "")
    title = title.replace("Transportation Research Part D", "")
    title = title.replace("Transportation Research Part C", "")
    title = title.replace("Transportation Research Part B", "")
    title = title.replace("Transportation Research Part A", "")
    title = title.replace("TransportationResearchPartB", "")
    title = title.replace("ScienceDirect", "")
    if(len(title) > 200 or len(title) < 5):
        title  = "Need manual check"

    print(title)
    remote_link = "https://scholar.google.com/scholar?q="+title.replace(" ", "%20")

    title = prefix + " " + title

    title_cell = {
        "cell_type": "markdown",
        "id": str(cell_id),
        "metadata": {},
        "source": [
        "### "+title+"\n",
        "<a href=\""+local_link+"\">PDF</a>" +"\n",
        "<a href=\""+remote_link+"\">Google Scholar</a>"
        ]
        }
    cell_id+=1

    if model is None:
        content_cell = {
            "cell_type": "markdown",
            "id": str(cell_id),
            "metadata": {},
            "source": [
            " "
            ]
        }
        cell_id+=1
    else:
        summary = summarize_text(html_text, model)
        print(summary)
        content_cell = {
            "cell_type": "markdown",
            "id": str(cell_id),
            "metadata": {},
            "source": [
            summary
            ]
        }
        
    cells.append(title_cell)
    cells.append(content_cell)

    return cells

def extract_folder(input_folder, res_links, recursive = False, model = None, prefix = ""):
    cells = []
    for paper in os.listdir(input_folder):
        local_link = input_folder + paper
        if paper.endswith(".pdf") and local_link not in res_links:
            cells += extract_cell(local_link, model, prefix = prefix)
        elif os.path.isdir(input_folder + paper) and recursive:
            cells += extract_folder(input_folder + paper + "/", res_links, recursive, model, prefix + "_" + paper)
    return cells

# Remove the style tag from the pdf
def extract_text(html_text):
    soup = BeautifulSoup(html_text, features="html.parser")
    spans = soup.find_all('span',style=True)

    res_text = []
    for span in spans:
        res_text.append(span.text)
    
    return truncate_text(''.join(res_text).strip())

def truncate_text(text: str, max_tokens=4000): # LLAMA3 has a max token limit of 8000, but we want to leave some room for more granular tokenization
    tokens = text.split(" ")  # crude tokenization
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return " ".join(tokens)

def summarize_text(html_text, model):
    document = extract_text(html_text)
    messages = [{"role": "system", "content": "I want you briefly summarize the paper in 250 words, including its research question, key methods, contributions, and results."},\
                {"role": "user", "content": f"{document}"}]
    terminators = [
    model.tokenizer.eos_token_id,
    model.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    outputs = model(
        messages,
        max_new_tokens=1024,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )

    return outputs[0]["generated_text"][-1]['content'].strip()

# Try to load the notebook in the traget directory
if __name__ == '__main__':
    # Check the system
    if platform.system() == "Windows":
        splitter = "\\"
    else:
        splitter = "/"
    # Configuration
    args = get_arguments(sys.argv[1:])

    # Load the GPT model
    if args.gpt:
        import transformers
        import torch
        # Load the model
        model = transformers.pipeline(
            "text-generation",
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="cuda",
        )
        
    else:
        model = None

    input_folder = args.input_folder
    name = args.name

    print("Your input folder is " + input_folder)

    if input_folder == "":
        print("Input folder cannot be empty")

    if not input_folder.endswith(splitter):
        input_folder += splitter

    if platform.system() == "Windows": input_folder = input_folder.replace("\\\\", "\\")

    output_folder = splitter.join(input_folder.split(splitter)[:-4]) # this -4 is hard coded, need to be changed according to the relative path between notebook and pdfs

    local_dir =  '/'.join(input_folder.split(splitter)[-4:])  # local dir need not to be changed accroding to the system

    if name == "":
        name = input_folder.split(splitter)[-2]

    print("Your output file is " + output_folder + splitter+ name + ".ipynb")

    # Get all the files in the folder
    res_links = []
    if(os.path.isfile(output_folder + splitter + name+".ipynb")):
        with open(output_folder + splitter + name+".ipynb", 'r', encoding="utf8") as f:
            res = json.load(f)

        print(res)

        if len(res['cells']) > 0:
            cell_id = int(res['cells'][-1]['id']) + 1
            res_links = [cell['source'][1][9:-10] for cell in res['cells'] if cell['source'][0].startswith("###")]
        else:
            cell_id = 0
    else:
        res = { "cells": [], 
           "metadata": {
              "kernelspec": {
               "display_name": "Python 3 (ipykernel)",
               "language": "python",
               "name": "python3"
               },
              "language_info": {
               "codemirror_mode": {
                "name": "ipython",
                "version": 3
               },
               "file_extension": ".py",
               "mimetype": "text/x-python",
               "name": "python",
               "nbconvert_exporter": "python",
               "pygments_lexer": "ipython3",
               "version": "3.8.8"
              }
            },
            "nbformat": 4,
            "nbformat_minor": 5
        }
        cell_id = 0

    # Make this a recursive search for subfolders when -r is set to True            
    res['cells'] += extract_folder(local_dir, res_links, args.recursive, model)
    
    # Save the notebook
    with open(output_folder+"/" + name+".ipynb", 'w') as f:
        json.dump(res, f)




