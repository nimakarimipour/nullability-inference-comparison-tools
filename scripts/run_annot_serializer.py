'''
This script runs error-prone on all the benchmarks.
Fill in the correct values for the macros at
the top of the file before executing.
'''
import os
import shutil

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
SOURCE = "wpi"
BENCHMARKS_FOLDER = f"../{SOURCE}"
RESULTS_FOLDER = f"compilation/{SOURCE}"
COMPILED_CLASSES_FOLDER = "classes"
SRC_FILES = "srcs.txt"
ERRORPRONE_DIR = "tools/error_prone"
ANNOTATOR_DIR = "tools/annotator"
CHECKER_DIR = "tools/cf"
ANNOTATOR_OUT = f"{CURRENT_DIR}/annotator-out"
ERRORPRONE_JARS = f'{ERRORPRONE_DIR}/error_prone_core-2.5.1-with-dependencies.jar:{ANNOTATOR_DIR}/annotLocator.jar'
ERRORPRONE_COMMAND = f"-XDcompilePolicy=simple -processorpath {ERRORPRONE_JARS} '-Xplugin:ErrorProne -XepDisableAllChecks -Xep:AnnotLocator:ERROR'"
SKIP_COMPLETED = False #skips if the output file is already there.
TIMEOUT = 1800
TIMEOUT_CMD = "timeout"

def prepare():
    shutil.rmtree(ANNOTATOR_OUT)
    os.makedirs(ANNOTATOR_OUT, exist_ok=True)
    with open(f'{ANNOTATOR_OUT}/paths.tsv', 'w') as o:
        o.write("{}\t{}\n".format(f'{ANNOTATOR_OUT}/checker.xml', f'{ANNOTATOR_OUT}/scanner.xml'))
        
        
# create results folder
if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)        

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
# make a directory for the annotations
os.system("mkdir annotations/{}".format(SOURCE))

for benchmark in os.listdir(BENCHMARKS_FOLDER):    
    if benchmark in to_skip:
        print(f"Skipping incompatible benchmark: {benchmark}")
        continue
    print("working on: " + benchmark)
    if (SKIP_COMPLETED):
        if os.path.exists(f'{RESULTS_FOLDER}/{benchmark}-after.txt'):
            print("skipping completed benchmark.")
            continue
    #skip non-directories
    if not os.path.isdir(f'{BENCHMARKS_FOLDER}/{benchmark}'):
        continue
    
    #create a folder for the compiled classes if it doesn't exist
    if not os.path.exists(COMPILED_CLASSES_FOLDER):
        os.mkdir(COMPILED_CLASSES_FOLDER)

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
    lib_folder = f'../original/{benchmark}/lib:{ERRORPRONE_DIR}/nullaway-annotations-0.10.22.jar:{ERRORPRONE_DIR}/jsr305-3.0.1.jar:{CHECKER_DIR}/checker/dist/checker-qual.jar'

    #build again
    build_command = (TIMEOUT_CMD 
        + " " + str(TIMEOUT)
        + " " + "javac -d"
        + " " + COMPILED_CLASSES_FOLDER
        + " " + " -cp " + lib_folder
        + " " + ERRORPRONE_COMMAND
        + " " + "-Xmaxerrs 10000" 
        + " " + "-J-Xmx32G"
        + " @" + SRC_FILES
        # + " 2> /dev/null"
        + " 2> " +  RESULTS_FOLDER
        + "/" + benchmark + ".txt"
    )
    # print(build_command)
    os.system("rm /tmp/annot-locator-out/nullable_elements.tsv > /dev/null 2>&1")
    os.system(build_command)
    if not os.path.exists("/tmp/annot-locator-out/nullable_elements.tsv"):
        print("compilation failed for: {}".format(benchmark))
    mv_command = "mv /tmp/annot-locator-out/nullable_elements.tsv annotations/{}/{}.tsv".format(SOURCE, benchmark)
    os.system(mv_command)
print("All benchmarks completed")