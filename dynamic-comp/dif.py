import os

root = "/Users/nima/Developer/njr/dynamic-comp"

def get_from_physical(benchmark, tool):
    path = f"/Users/nima/Developer/njr/scripts/annotations/{tool}/" + benchmark + ".tsv"
    if not os.path.exists(path):
        return []
    lines = open(path, "r").readlines()[1:]
    lines = [x[:x.index("/home/nima/") - 1].strip() for x in lines]
    lines = [x.replace("$", ".") for x in lines]
    return lines

# read content of java_11_incompatible.txt
java_11_incompatible = []
with open('../java_11_incompatible.txt', 'r') as file:
    java_11_incompatible = file.read().splitlines()
    

all_miss = {}
difffs = {}
for tool in ["wpi", "nullgtn", "annotator"]:
    all_miss[tool] = []
    difffs[tool] = {}


to_skip = java_11_incompatible

cnt = 0
miss_cnt = {}
for tool in ["wpi", "nullgtn", "annotator"]:
    miss_cnt[tool] = 0


skip_annot = 0
def for_tool(tool):
    global cnt, skip_annot
    tool_incompatible = []
    with open(f'../{tool}_incompatible.txt', 'r') as file:
        tool_incompatible = file.read().splitlines()
    data = []
    # read traces annot
    for dirpath, _, filenames in os.walk(root + "/traces"):
        if(os.path.exists(dirpath + "/serialized.txt") == False):
            continue
        from_trace = set(open(dirpath + "/" + "serialized.txt").readlines())
        from_trace = [x.strip() for x in from_trace]
        from_trace = [x.replace("$", ".") for x in from_trace]
        cnt += len(from_trace)
        if len(from_trace) == 0:
            continue
        from_trace = set([x.strip() for x in from_trace])
        benchmark = dirpath.split("/")[-1]
        if benchmark in to_skip:
            continue
        if benchmark in tool_incompatible:
            data.append(0)
            continue
        from_physical = set(get_from_physical(benchmark, tool))

        diff = from_trace - from_physical
        percentage = (len(diff) * 1.0) / len(from_trace) * 100
        if len(diff) > 0:
            difffs[tool][benchmark] = diff
            miss_cnt[tool] += len(diff)
        data.append(percentage)
    return data
wpi_data = sorted(for_tool("wpi"))
nullgtn_data = sorted(for_tool("nullgtn"))
annotator_data = sorted(for_tool("annotator"))

wpi_data = [round(x, 2) for x in wpi_data]
nullgtn_data = [round(x, 2) for x in nullgtn_data]
annotator_data = [round(x, 2) for x in annotator_data]

# show wpi_data and nullgtn_data and annotator_data in one histogram
import matplotlib.pyplot as plt
import numpy as np

bins = np.arange(0, 110, 10)

# Calculate the frequency of each series within the bins
freq_data1, _ = np.histogram(wpi_data, bins=bins)
freq_data2, _ = np.histogram(nullgtn_data, bins=bins)
freq_data3, _ = np.histogram(annotator_data, bins=bins)

# Create a grouped bar chart
bar_width = 0.2  # Width of the bars
index = np.arange(len(freq_data1))  # The x locations for the groups

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 4))

# Plot bars for each data series
bar1 = ax.bar(index, freq_data1, bar_width, label='WPI')
bar2 = ax.bar(index + bar_width, freq_data2, bar_width, label='NullGtn')
bar3 = ax.bar(index + 2 * bar_width, freq_data3, bar_width, label='Annotator')

# Add labels and title
ax.set_xlabel('Percentage of missed annotations from traces')
ax.set_ylabel('Number of benchmarks')
ax.set_xticks(index + bar_width)
ax.set_xticklabels([f'{i}-{i+10}%' for i in bins[:-1]])

# Add legend
ax.legend()

# Display the plot
plt.tight_layout()

plt.savefig('/Users/nima/Desktop/grouped_bar_chart.pdf', format='pdf')

plt.show()


# wpi_miss = all_miss["wpi"]
# nullgtn_all_miss = all_miss["nullgtn"]
# annotator_all_miss = all_miss["annotator"]

# #intersection of all three
# intersection = set(wpi_miss) & set(nullgtn_all_miss) & set(annotator_all_miss)
# for x in intersection:
#     print(x)

miss_wpi = miss_cnt["wpi"]
miss_annotator = miss_cnt["annotator"] - 2
miss_nullgtn = miss_cnt["nullgtn"]


print("cnt:{}".format(cnt))
print("wpi:{} - {} - {}".format(miss_wpi, cnt - miss_wpi, ((cnt - miss_wpi) / cnt) * 100))
print("nullgtn:{} - {} - {}".format(miss_nullgtn, cnt - miss_nullgtn, ((cnt - miss_nullgtn) / cnt) * 100))
print("annotator:{} - {} - {}".format(miss_annotator, cnt - miss_annotator, ((cnt - miss_annotator) / cnt) * 100))
