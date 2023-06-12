#!/usr/bin/env python
# coding: utf-8

import os
import sys
from bs4 import BeautifulSoup
import re
import json
import argparse
import platform

def get_arguments(argv):
    parser = argparse.ArgumentParser(description='PyBib Cleaner')
    # Simulation settings
    parser.add_argument('-i', '--input_folder', default="")
    parser.add_argument('-n', '--name', default="")
    args = parser.parse_args(argv)

    return args


# Try to load the notebook in the traget directory
if __name__ == '__main__':
    # Check the system
    if platform.system() == "Windows":
        splitter = "\\"
    else:
        splitter = "/"

    # Configuration
    args = get_arguments(sys.argv[1:])

    input_folder = args.input_folder
    name = args.name

    print("Your input folder is " + input_folder)

    if input_folder == "":
        print("Input folder cannot be empty")

    if not input_folder.endswith(splitter):
        input_folder += splitter

    if platform.system() == "Windows": input_folder = input_folder.replace("\\\\", "\\")

    output_folder = splitter.join(input_folder.split(splitter)[:-4])

    local_dir =  '/'.join(input_folder.split(splitter)[-4:])  # local dir need not to be changed accroding to the system

    if name == "":
        name = input_folder.split(splitter)[-2]

    print("Your output file is " + output_folder + splitter+ name + ".ipynb")

    # Get all the files in the folder
    res_links = []
    if(os.path.isfile(output_folder+"/" + name+".ipynb")):
        with open(output_folder+"/" + name+".ipynb", 'r', encoding="utf8") as f:
            res = json.load(f)
        cell_id = int(res['cells'][-1]['id']) + 1
        res_links = [cell['source'][1][9:-10] for cell in res['cells'] if cell['source'][0].startswith("###")]
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
    
    for paper in os.listdir(input_folder):
        local_link = local_dir + paper
        if local_link not in res_links:
            # delete the paper since it is not in the notebook after we have updated the notebook
            if os.path.isfile(input_folder + paper):
                os.remove(input_folder + paper)
                print("Deleting " + input_folder + paper)








