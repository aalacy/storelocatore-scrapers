import os
import shutil

src_dir = os.getcwd()
print(src_dir)
dest = "\\".join(src_dir.split("\\")[0:-3]) + "\\storelocator\\"
print(dest)

files_to_copy = ["scrape.py", "requirements.txt", "SUCCESS"]
folders = [
    "joefresh_com",
    "freshmart_ca",
    "shopeasy_ca",
    "extrafoods_ca",
    "newfoundlandgrocerystores_ca",
    "fortinos_ca",
    "axep_ca",
    "yourindependentgrocer_ca",
    "independentcitymarket_ca",
    "nofrills_ca",
    "atlanticsuperstore_ca",
    "maxi_ca",
    "valumart_ca",
    "wholesaleclub_ca",
    "loblaws_com",
    "zehrs_ca",
    "realcanadiansuperstore_ca",
    "lintermarche_ca",
    "provigo_ca",
    "wellwise_ca",
    "realcanadianliquorstore_ca",
    "shoppersdrugmart_ca",
]

print("Copying ", len(files_to_copy), " files to ", len(folders), " locations")
for i in folders:
    for j in files_to_copy:
        shutil.copy2(src_dir + "\\" + str(j), dest + i + "\\")
