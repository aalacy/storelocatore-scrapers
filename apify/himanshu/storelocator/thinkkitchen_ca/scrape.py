import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thinkkitchen_ca')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
  
    base_url= "http://thinkkitchen.ca/en/storelocator.php"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object=[]
    k = soup.find("div",{'class':"layer1"}).find_all("div",{"class":"content","id":"laye1i"})[:7]
    for i in k:
        st = i.text.replace("  ","").strip().replace("\n",",").split(",,")
        for j in range(len(st)):
            tem_var=[]
            v = st[j].split(",")
            if v[0]==' ':
                del v[0]
            if len(v)==2:
                name = (v[0])
                full_address1 = v[-1].split("Mon")[0].encode('ascii', 'ignore').decode('ascii').strip().replace("(","").replace(")"," ").replace("?","")
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(full_address1))[-1]
                zip1 = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address1))[-1]
                state_list = re.findall(r' ([A-Z]{2}) ', str(full_address1))[-1]
                address = full_address1.replace(phone_list,"").replace(zip1,"").replace(state_list,"").split("  ")[0].replace("Winnipeg","")
                city = (full_address1.replace(phone_list,"").replace(zip1,"").replace(state_list,"").replace(address,"").strip()).strip()
                hours = (" ".join(v[-1].split("Mon")[1:]).replace(".-","Mon-").replace(". - ","Mon-").replace("?","").replace("|"," ").encode('ascii', 'ignore').decode('ascii').strip())
            if len(v)==3:
                name = (v[0])
                full_address =(v[-1].split("Mon")[0].encode('ascii', 'ignore').decode('ascii').strip().replace("?","").replace("("," ").replace(")"," ").replace("BCV4M 0B3","BC  V4M 0B3"))
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address))
                state_list = re.findall(r' ([A-Z]{2}) ', str(full_address))
                hours_list = (v[-1].split("Mon")[1:])
                if hours_list:
                    hours  =" ".join(hours_list).replace(". - ","Mon ").replace(".-","Mon").replace("-Wed","Mon-Wed").replace("|"," ").replace("?","").replace("  "," ").replace("/","").encode('ascii', 'ignore').decode('ascii').strip()
                
                zip1 = (ca_zip_list[-1])
                if state_list:
                    state = state_list[-1]
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(full_address))[-1]
                city = full_address.replace(phone_list,"").replace(state,"").replace(zip1,"").replace("Boulevard Laurier ","<MISSING>").replace("Sault Ste. ","").replace("BC","<MISSING>").strip()
                address = (v[1:][0].replace("2700","2700, Boulevard Laurier").replace("293 Bay Street","293 Bay Street, Sault Ste").encode('ascii', 'ignore').decode('ascii').strip())
 
  
            tem_var.append("http://thinkkitchen.ca")
            tem_var.append(name.replace("\n","").strip().lstrip())
            tem_var.append(address)
            tem_var.append(city)
            tem_var.append(state.replace(".",""))
            tem_var.append(zip1)
            tem_var.append("CA")
            tem_var.append("<MISSING>")
            tem_var.append(phone_list)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours if hours else "<MISSING>")
            tem_var.append("http://thinkkitchen.ca/en/storelocator.php")
            # logger.info(tem_var)
            return_main_object.append(tem_var)
   
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




