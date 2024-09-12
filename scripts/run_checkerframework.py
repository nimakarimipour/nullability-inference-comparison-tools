'''
This script runs checker-framework on all the benchmarks.
Fill in the correct values for the macros at
the top of the file before executing.
'''
import os

SOURCE = "wpi"
BENCHMARKS_FOLDER = f"../{SOURCE}"
RESULTS_FOLDER = f"nullness/{SOURCE}"
COMPILED_CLASSES_FOLDER = "classes"
SRC_FILES = "srcs.txt"
CF_BINARY = "tools/cf/checker/bin/javac"
CHECKER_DIR = "tools/cf"
CF_COMMAND = "-processor org.checkerframework.checker.nullness.NullnessChecker"
SKIP_COMPLETED = False #skips if the output file is already there.
TIMEOUT = 1800
TIMEOUT_CMD = "timeout"

#create the output folder if it doesn't exist
if not os.path.exists(RESULTS_FOLDER):
    os.mkdir(RESULTS_FOLDER)

# read content of java_11_incompatible.txt
java_11_incompatible = []
with open('../java_11_incompatible.txt', 'r') as file:
    java_11_incompatible = file.read().splitlines()
    
tool_incompatible = []
with open('../{}_incompatible.txt'.format(SOURCE), 'r') as file:
    tool_incompatible = file.read().splitlines()
    tool_incompatible = [x.split(" ")[0] for x in tool_incompatible]

to_skip = java_11_incompatible + tool_incompatible

#Loop through the benchmarks
print("Completed Benchmarks")
for benchmark in os.listdir(BENCHMARKS_FOLDER):
    
    if benchmark in to_skip:
        print(f"Skipping incompatible benchmark: {benchmark}")
        continue
    
    if (SKIP_COMPLETED):
        if os.path.exists(f'{RESULTS_FOLDER}/{benchmark}.txt'):
            print("skipping completed benchmark.")
            continue
    #skip non-directories
    if not os.path.isdir(f'{BENCHMARKS_FOLDER}/{benchmark}'):
        continue
    
    #create a folder for the compiled classes if it doesn't exist
    if not os.path.exists(COMPILED_CLASSES_FOLDER):
        os.mkdir(COMPILED_CLASSES_FOLDER)
    
    print("working on: " + benchmark)    

    #Get a list of Java source code files.
    find_srcs_command = f'find {BENCHMARKS_FOLDER}/{benchmark}/src -name "*.java" > {SRC_FILES}'
    os.system(find_srcs_command)
    
    # just for wpi
    if SOURCE == "wpi":
        find_org_srcs_command = f'find ../original/{benchmark}/src -name "*.java" > original_srcs.txt'
        os.system(find_org_srcs_command)
        wpi_srcs = open(SRC_FILES, 'r').read().splitlines()
        org_srcs = open('original_srcs.txt', 'r').read().splitlines()
        left_out = []
        for src in org_srcs:
            replaced = src.replace('../original/', '../wpi/')
            if replaced not in wpi_srcs:
                left_out.append(src)  
        # append left out files to SRC_FILES
        with open(SRC_FILES, 'a') as f:
            for src in left_out:
                f.write(src + '\n')

    #get folder with libraries used by benchmark
    lib_folder = f'../original/{benchmark}/lib:{CHECKER_DIR}/checker/dist/checker-qual.jar'

    #execute infer on the source files
    command = (TIMEOUT_CMD 
        + " " + str(TIMEOUT)
        + " " + CF_BINARY
        + " " + CF_COMMAND
        + " " + "-d"
        + " " + COMPILED_CLASSES_FOLDER
        + " " + "-Xmaxerrs 100000" 
        + " " + "-J-Xmx32G"
        + " " + " -cp " + lib_folder 
        + " @" + SRC_FILES
        + " 2> " +  RESULTS_FOLDER
        + "/" + benchmark + ".txt"
    )
    os.system(command)
    
print("All benchmarks completed")
