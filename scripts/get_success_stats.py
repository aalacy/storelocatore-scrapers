import re
import pandas as pd
from pathlib import Path
from ast import literal_eval
import collections
from pprint import pprint
import termcolor

res = []

def getHighestVersionUsed(contents):
	results = re.findall(r"0.0.\d{1,2}", str(contents))
	if results:
		return sorted(results, key=lambda x: int(x[4:]))[-1]
	return ""

def getIgnored(contents):
	contents = str(contents)
	if "--ignore" in contents and "PYTHON_VERSION" in contents:
		idx = contents.index("--ignore")
		newString = contents[idx:]
		mapped = map(lambda x: x.replace("\\n", "").replace("\"", "").replace("',", ""), 
			newString[9:newString.index("PYTHON_VERSION")].strip().split(" "))
		filtered = filter(lambda x: len(x) > 2 and "ignore" not in x, mapped)
		return list(filtered)
	return None

def getAuthor(fname):
	return str(fname).split("/")[1]

fnames = [fname for fname in Path('.').glob('**/SUCCESS')]
contentsList = []
for fname in fnames:
	with open(fname, "r") as f:
		contentsList.append((fname, f.readlines()))

for fname, contents in contentsList:
	res.append({
		"filename": fname,
		"author": getAuthor(fname),
		"contents": contents,
		"version": getHighestVersionUsed(contents),
		"ignored": getIgnored(contents)
	})

df = pd.DataFrame(res)[["filename", "author", "contents", "version", "ignored"]]

print(termcolor.colored("==============================", "red"))
print(termcolor.colored("Num files total: {}".format(len(fnames)), "red"))
print(termcolor.colored("Num files with non-empty SUCCESS file: {}".format(len(df[df["contents"].str.len() > 0])), "red"))
print(termcolor.colored("Num files with at least 1 check skipped: {}".format(len(df[df["ignored"].notnull()])), "red"))

def printIgnoredChecksInSortedOrder():
	ignored = df[df["ignored"].notnull()]["ignored"]
	everyIgnoreFlagged = ignored.sum()
	counter = collections.Counter(everyIgnoreFlagged)
	pprint(counter.most_common())

def printValueCountsForColumn(col):
	print(df[col].value_counts())

print(termcolor.colored("Printing ignored checked in sorted order", "red", on_color="on_white", attrs=["reverse"]))
printIgnoredChecksInSortedOrder()

print(termcolor.colored("Printing author counts", "red", on_color="on_white", attrs=["reverse"]))
printValueCountsForColumn("author")

print(termcolor.colored("Printing version counts", "red", on_color="on_white", attrs=["reverse"]))
printValueCountsForColumn("version")
