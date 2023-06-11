import os
import sys
import argparse

# convert the Python notebook to pdf
def get_arguments(argv):
    parser = argparse.ArgumentParser(description='PyBib')
    # Simulation settings
    parser.add_argument('-i', '--input_file', default="")
    args = parser.parse_args(argv)

    return args


if __name__ == '__main__':
    # Configuration
    args = get_arguments(sys.argv[1:])

    input = args.input_file.replace("\\\\", "/")

    os.system(f'jupyter nbconvert --to html "{input}"')

    html_input = input.replace(".ipynb", ".html")
    pdf_output = input.replace(".ipynb", "") + ".pdf"

    command = f'wkhtmltopdf --enable-local-file-access "{html_input}" "{pdf_output}"'
    os.system(command)
    os.remove(html_input)