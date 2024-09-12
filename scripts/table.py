import os
import re


def read_annottaion_num(benchmark, tool):
    path = f'annotations/{tool}/{benchmark}.tsv'
    if not os.path.exists(path):
        return "-"
    return str(len(open(path, "r").readlines()) - 1)


def deduction(base, result, index=0):
    if base == "-" or result == "-":
        return "-"
    base = int(base)
    result = int(result)
    if base == 0:
        return "-"
    return round((base - result) / base * 100, 2)


def read_error(checker, benchmark, tool):
    path = f'{checker}/{tool}/{benchmark}.txt'
    if not os.path.exists(path):
        return "-"
    content = open(path, "r").read()
    if "symbol not found" in content:
        return "-"
    lines = content.split("\n")
    # traverse in reverse order
    for i in range(len(lines) - 1, -1, -1):
        l = lines[i]
        # check if line is in format with regex "x errors" and return x
        if re.match(r"\d+ errors", l):
            return l.split(" ")[0]
    return 0

initial = {}
lines = open("benchmarks.csv", "r").readlines()
lines = lines[1:]
lines = [l.strip() for l in lines]
for l in lines:
    parts = l.split(",")
    initial[parts[0]] = {"loc": parts[1], "nullaway": parts[2], "cf": parts[6]}
    
    
num = 0    
    
print("benchmark,loc,nullaway,nullaway-wpi,deduction,nullaway-annotator,deduction,nullaway-nullgtn,deduction,cf,cf-wpi,deduction,cf-annotator,deduction,cf-nullgtn,deduction,annot-wpi,annot-annotator,annot-nullgtn")
for benchmark in os.listdir("../original"):
    if benchmark not in initial:
        continue
    
    loc = initial[benchmark]["loc"]
    nullaway = read_error("nullaway", benchmark, "original")
    cf = read_error("nullness", benchmark, "original")
    
    annot_num_wpi = read_annottaion_num(benchmark, "wpi")
    annot_num_wpi_full = read_annottaion_num(benchmark, "wpi-full")
    annot_num_wpi_annotator = read_annottaion_num(benchmark, "annotator")
    annot_num_wpi_nullgtn = read_annottaion_num(benchmark, "nullgtn")
    
    nullaway_wpi = read_error("nullaway", benchmark, "wpi")
    nullaway_annotator = read_error("nullaway", benchmark, "annotator")
    nullaway_nullgtn = read_error("nullaway", benchmark, "nullgtn")
    
    cf_wpi = read_error("nullness", benchmark, "wpi")
    cf_annotator = read_error("nullness", benchmark, "annotator")
    cf_nullgtn = read_error("nullness", benchmark, "nullgtn")
    
    if nullaway == "-" and cf == "-":
        continue
    if cf_wpi != "-" and (int(cf) > int(cf_wpi)):
        num += 1 
        
    # print(f"{benchmark},{loc},{nullaway},{nullaway_wpi},{deduction(nullaway, nullaway_wpi, 0)},{nullaway_annotator},{deduction(nullaway, nullaway_annotator, 1)},{nullaway_nullgtn},{deduction(nullaway, nullaway_nullgtn, 2)},{cf},{cf_wpi},{deduction(cf, cf_wpi, 3)},{cf_annotator},{deduction(cf, cf_annotator, 4)},{cf_nullgtn},{deduction(cf, cf_nullgtn, 5)},{annot_num_wpi}/{annot_num_wpi_full},{annot_num_wpi_annotator},{annot_num_wpi_nullgtn}")
print(num)