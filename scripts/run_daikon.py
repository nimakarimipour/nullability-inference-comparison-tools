"""
This script executes all the benchmarks with no command line arguments.
Fill in the correct values for the macros at
the top of the file before executing.
"""

import os
import subprocess
import shlex

RESULTS_FOLDER = "results/daikon_execution_results"
JAVA_COMMAND = "java"
TIMEOUT = 10
FILE_WITH_MAIN_CLASS = "info/mainclassname"
SKIP_COMPLETED = False  # skips if the output file is already there.
CUR_DIR = os.getcwd()
BENCHMARKS_FOLDER = os.path.join(CUR_DIR, "../june2020_dataset")
DAIKONDIR = os.getenv("DAIKONDIR")

def execute(command):
    try:
        result = subprocess.run(
            command,
            timeout=TIMEOUT,
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd(),
        )
        print("Return code:", result.returncode)
    except subprocess.TimeoutExpired:
        print(f"Command '{command}' timed out after {TIMEOUT} seconds")
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with return code {e.returncode}")


# create the output folder if it doesn't exist
results_folder_path = os.path.join(CUR_DIR, RESULTS_FOLDER)
if not os.path.exists(results_folder_path):
    os.mkdir(results_folder_path)


# Loop through the benchmarks
print("Completed Benchmarks")
for benchmark in os.listdir(BENCHMARKS_FOLDER):
    # print(benchmark)
    if benchmark != "url0c7746c72b_wsuetholz_DiscountStrategy_tgz-pJ8-net_suetholz_pos_MainJ8":
        continue
    print("Processing Benchmark: ", benchmark)
    benchmark_results_folder = os.path.join(results_folder_path, benchmark)
    os.makedirs(benchmark_results_folder, exist_ok=True)

    # skip non-directories
    benchmark_path = os.path.join(BENCHMARKS_FOLDER, benchmark)
    if not os.path.isdir(benchmark_path):
        continue

    # Get jar file
    jarfile = ""
    for file in os.listdir(os.path.join(benchmark_path, "jarfile")):
        if file.endswith(".jar"):
            jarfile = file
    jarfile_path = os.path.join(benchmark_path, ("jarfile/" + jarfile))
    # get main class name
    mainclassname_file = os.path.join(benchmark_path, FILE_WITH_MAIN_CLASS)
    with open(mainclassname_file) as fp:
        mainclass_name = fp.read().splitlines()[0]
        
    execute("killall -9 java")   

    # first command: java -cp .:$DAIKONDIR/daikon.jar daikon.DynComp DataStructures.StackArTester
    run_command = (
        JAVA_COMMAND
        + " -cp "
        + jarfile_path
        + ":{}/daikon.jar".format(DAIKONDIR)
        + " "
        + "daikon.DynComp"
        + " "
        + mainclass_name
        # + " > "
        # + benchmark_results_folder
        # + "/1.txt 2>&1"
    )
    print(run_command)
    execute(run_command)

    # second command: java -cp .:$DAIKONDIR/daikon.jar daikon.Chicory --daikon --comparability-file=StackArTester.decls-DynComp DataStructures.StackArTester
    run_command = (
        JAVA_COMMAND
        + " -cp "
        + jarfile_path
        + ":{}/daikon.jar".format(DAIKONDIR)
        + " "
        + "daikon.Chicory --daikon --comparability-file="
        + mainclass_name.split(".")[-1]
        + ".decls-DynComp"
        + " "
        + mainclass_name
        # + " > "
        # + benchmark_results_folder
        # + "/2.txt 2>&1 "
    )
    print(run_command)
    execute(run_command)
    # execute("mv *.dtrace.gz {}".format(benchmark_results_folder))
    # execute("mv *.decls-DynComp {}".format(benchmark_results_folder))
