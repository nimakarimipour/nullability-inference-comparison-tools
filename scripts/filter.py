import os

# root dir
root_dir = "/Users/nima/Desktop/njr/scripts/results/daikon_execution_results"

# walk through the root dir
for dir, dirs, files in os.walk(root_dir):
    if dir == root_dir:
        continue
    contains_decl = False
    for file in files:
        if file.endswith(".decls-DynComp"):
            contains_decl = True
            break
    contains_trace = ":::" in open(dir + "/2.txt", 'r').read()
    if contains_decl and contains_trace:
        continue
    if contains_decl and not contains_trace:
        print(dir)