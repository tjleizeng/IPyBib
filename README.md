# PyBib
This is a simple Yython script for automated generating lists for literature.

The input is the folder with a bunch of PDF files (your literature), and the output is an IPython Notebook with links to local files and google scholar links.

I am using the following structure to maintain my files: "[top folder]/pdf/[year]/[topic]/". Hence, in the script I cut the output_folder at location "-4" (line 61 and line 63). You can change it based on your needs. 

Finally, note the title inference may fail, but you can always correct it in the generated notebook :)
