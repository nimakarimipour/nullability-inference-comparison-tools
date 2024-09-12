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
RESULTS_FOLDER = f"nullaway/{SOURCE}"
COMPILED_CLASSES_FOLDER = "classes"
SRC_FILES = "srcs.txt"
ERRORPRONE_DIR = "tools/error_prone"
CHECKER_DIR = "tools/cf"
ANNOTATOR_DIR = "tools/annotator"
ANNOTATOR_OUT = f"{CURRENT_DIR}/annotator-out"
ERRORPRONE_JARS = f'{ERRORPRONE_DIR}/error_prone_core-2.5.1-with-dependencies.jar:{ERRORPRONE_DIR}/dataflow-nullaway-3.26.0.jar:{ERRORPRONE_DIR}/nullaway-0.10.10.jar:{ANNOTATOR_DIR}/annotLocator.jar:{CHECKER_DIR}/checker/dist/checker-qual.jar'
ERRORPRONE_COMMAND = f"-XDcompilePolicy=simple -processorpath {ERRORPRONE_JARS} '-Xplugin:ErrorProne -XepDisableAllChecks -Xep:AnnotLocator:ERROR -Xep:NullAway:ERROR -XepOpt:NullAway:AnnotatedPackages="
SKIP_COMPLETED = False #skips if the output file is already there.
TIMEOUT = 1800
TIMEOUT_CMD = "timeout"
ANNOTATOR_JAR = f'{CURRENT_DIR}/{ANNOTATOR_DIR}/annotator.jar'

def prepare():
    shutil.rmtree(ANNOTATOR_OUT)
    os.makedirs(ANNOTATOR_OUT, exist_ok=True)
    with open(f'{ANNOTATOR_OUT}/paths.tsv', 'w') as o:
        o.write("{}\t{}\n".format(f'{ANNOTATOR_OUT}/checker.xml', f'{ANNOTATOR_OUT}/scanner.xml'))

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
        if os.path.exists(f'{RESULTS_FOLDER}/{benchmark}-after.txt'):
            print("skipping completed benchmark.")
            continue
    #skip non-directories
    if not os.path.isdir(f'{BENCHMARKS_FOLDER}/{benchmark}'):
        continue

    print("working on: " + benchmark)
    
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

    src = open(f'../original/{benchmark}/info/sources', "r").readlines()
    src = [x.strip() for x in src]
    src = [x[4:x.rfind("/")] for x in src]
    src = [x.replace("/", ".") for x in src]
    src = set(src)
    if '' in src:
        src.remove('')
    src = ",".join(src)
    if(src == ""):
        continue

    #get folder with libraries used by benchmark
    lib_folder = f'../original/{benchmark}/lib:{ERRORPRONE_DIR}/nullaway-annotations-0.10.22.jar:{ERRORPRONE_DIR}/jsr305-3.0.1.jar:{CHECKER_DIR}/checker/dist/checker-qual.jar'

    #build again
    build_command = (TIMEOUT_CMD 
        + " " + str(TIMEOUT)
        + " " + "javac -d"
        + " " + COMPILED_CLASSES_FOLDER
        + " " + " -cp " + lib_folder
        + " " + ERRORPRONE_COMMAND + src + "'"
        + " " + "-Xmaxerrs 10000" 
        + " " + "-J-Xmx32G"
        + " @" + SRC_FILES
        + " 2> " +  RESULTS_FOLDER
        + "/" + benchmark + ".txt"
    )
    os.system("rm /tmp/annot-locator-out/nullable_elements.tsv > /dev/null 2>&1")
    os.system(build_command)
    if not os.path.exists("/tmp/annot-locator-out/nullable_elements.tsv"):
        print("compilation failed for: {}".format(benchmark))

print("All benchmarks completed")