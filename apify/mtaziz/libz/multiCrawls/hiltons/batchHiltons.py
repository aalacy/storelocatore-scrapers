import os
import shutil

src_dir = os.getcwd()
dest = "\\".join(src_dir.split("\\")[0:-3]) + "\\storelocator\\"

files_to_copy = ["scrape.py", "requirements.txt", "SUCCESS", "Dockerfile", "README.md"]
folders = [
    "hilton_co_uk",
    "conradhotels3_hilton_com",
    "tru3_hilton_com",
    "hamptoninn_com",
    "waldorfastoria3_hilton_com",
    "homewoodsuites3_hilton_com",
    "home2suites3_hilton_com",
    "doubletree3_hilton_com",
    "hilton_com__en__motto",
    "lxrhotels3_hilton_com",
    "hiltongardeninn3_hilton_com",
    "hilton_com__en__tapestry",
    "embassysuites3_hilton_com",
    "curiocollection3_hilton_com",
    "waldorfastoria3_hilton_com",
]

for i in folders:
    for j in files_to_copy:
        if not os.path.exists(dest + str(i) + "\\"):
            os.mkdir(dest + str(i) + "\\")
        shutil.copy2(src_dir + "\\" + str(j), dest + i + "\\")
