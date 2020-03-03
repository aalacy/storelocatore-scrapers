import os
import codecs
import re

wf = codecs.open(r"C:\Users\Aleena Haider\Desktop\Transcription.txt","w",encoding="utf-8") #main file
files=os.listdir("F:\datasets\Transcription")#transcription files folder

for file in files:
    f = codecs.open(r"F:\datasets\Transcription\\"+file, "r", encoding="utf-8")
    lines=f.readlines()
    for line in lines:
        line = line.strip()
        l = re.findall(r'[A-Z0-9]+',line)[0]
        lr = line.replace(l,"")
        if lr != "":
            wf.write(line+"\n")
        else:
            print (l)
    f.close()
wf.close()
