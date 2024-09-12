import os

ANNOTATION_DIR = '/Users/nima/Developer/njr/scripts/annotations'

java_11_incompatible = []
with open('../../java_11_incompatible.txt', 'r') as file:
    java_11_incompatible = file.read().splitlines()
    

def read_incompatible(tool):
    tool_incompatible = []
    with open('../../{}_incompatible.txt'.format(tool), 'r') as file:
        tool_incompatible = file.read().splitlines()
        tool_incompatible = [x.split(" ")[0] for x in tool_incompatible]
    return tool_incompatible

to_skip = java_11_incompatible
to_skip.extend(read_incompatible('annotator'))
to_skip.extend(read_incompatible('wpi'))
to_skip.extend(read_incompatible('nullgtn'))


def check_annot_in_wpi(annot):
    path = annot.split("\t")[5]
    wpi_root = "/Users/nima/Developer/njr/wpi/{}".format(path)
    return os.path.exists(wpi_root)


def read_all_annotation(tool):
    all_annots = []
    dir = os.path.join(ANNOTATION_DIR, tool)
    root_path = "/home/nima/Developer/NJR-ANNOTATED-RUN/{}/".format(tool)
    # read all files in the directory
    for file in os.listdir(dir):
        if file[:-4] in to_skip:
            continue
        annots = open(os.path.join(dir, file), 'r').readlines()
        annots = [a.strip() for a in annots]
        annots = [a.replace(root_path, "") for a in annots]
        annots = [a for a in annots if check_annot_in_wpi(a)]
        all_annots.extend(annots)
    return set(all_annots)


annotator_annots = read_all_annotation('annotator')
wpi_annots = read_all_annotation('wpi')
nullgtn_annots = read_all_annotation('nullgtn')

# # find annotations that only exists in one of them
# only_annotator = annotator_annots - wpi_annots - nullgtn_annots
# # add the name annotator to each element in the set
# # only_annotator = set([f'{a}\tannotator' for a in only_annotator])


# only_wpi = wpi_annots - annotator_annots - nullgtn_annots
# # only_wpi = set([f'{a}\twpi' for a in only_wpi])

# only_nullgtn = nullgtn_annots - annotator_annots - wpi_annots
# # only_nullgtn = set([f'{a}\tnullgtn' for a in only_nullgtn])

annot_wpi = annotator_annots.intersection(wpi_annots) - nullgtn_annots
annot_wpi = set([f'{a}\t!nullgtn' for a in annot_wpi])

annot_nullgtn = annotator_annots.intersection(nullgtn_annots) - wpi_annots
annot_nullgtn = set([f'{a}\t!wpi' for a in annot_nullgtn])

wpi_nullgtn = wpi_annots.intersection(nullgtn_annots) - annotator_annots
wpi_annots = set([f'{a}\t!annotator' for a in wpi_nullgtn])

combined = annot_wpi.union(annot_nullgtn).union(wpi_annots)

for c in combined:
    print(c)