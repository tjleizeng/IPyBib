# IPyBib
These are Python scripts for generating a maintainable literature review documents from raw pdf files.

The input is the folder with a bunch of PDF files (no need to rename or organize it!), and the output is an IPython Notebook with links to local files and google scholar links.

I am using the following structure to maintain my files: "[top folder]/pdf/[year]/[topic]/". Hence, in the script I cut the output_folder at location "-4" (line 68 and line 70). You can change it if you adopt a different file structures. 

Finally, note the title inference may fail, but you can always correct it in the generated notebook :)
