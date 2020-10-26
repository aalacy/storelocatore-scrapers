import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import urllib3
import requests

session = SgRequests()

requests.packages.urllib3.disable_warnings()




def write_output(data):
    with open('data.csv', mode='w',newline = "") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url= "https://eat.co.uk/our-locations"
    r = session.get(base_url,verify=False, headers =headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    loc = soup.find_all("a",{"class":"platopusLink"})
    for data in loc:
        # us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(list(data.stripped_strings)[2]))
        # if us_zip_list:
        #     pass
        # else:
        country_code="UK"
        name = list(data.stripped_strings)[0]
        address = list(data.stripped_strings)[1]
        zip1 =list(data.stripped_strings)[2].split(",")[-1].replace("BART1","<MISSING>") 
        city = list(data.stripped_strings)[2].split(",")[0]
        len1 = list(data.stripped_strings)[2].split(",")
        if len(len1)==3:
            state = len1[1]
        else:
            state =  "<MISSING>"
        page_url = "https://eat.co.uk/"+data['href']
        store_number = page_url.split("_")[-1].strip()
        # print("https://eat.co.uk/"+data['href'])
        r1 = session.get("https://eat.co.uk"+data['href'],verify=False, headers =headers)
        soup1= BeautifulSoup(r1.text,"lxml")
        hours = " ".join(list(soup1.find("table",{"class":"platopusOpeningHoursTable"}).stripped_strings)).replace("Opening Times","").strip()
        lat = soup1.find("a",{"class":"align-center dmButtonLink dmWidget dmWwr default dmOnlyButton dmDefaultGradient u_1454164222"})['href'].split("=")[-1].split(",")[0]
        log = soup1.find("a",{"class":"align-center dmButtonLink dmWidget dmWwr default dmOnlyButton dmDefaultGradient u_1454164222"})['href'].split("=")[-1].split(",")[1]
        if lat=="0":
            lat = "<MISSING>"
            log = "<MISSING>"
        if city in ["Barcelona","Madrid"]   :
        	country_code = "es"
        if "El Altet" in state	:
        	country_code	= "es"
        if "Paris" in city:
            country_code = "fr"
        tem_var =[]
        tem_var.append("https://eat.co.uk")
        tem_var.append(name)
        tem_var.append(address.replace(",",""))
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append(country_code)
        tem_var.append(store_number)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(log)
        tem_var.append(hours)
        tem_var.append(page_url)
        tem_var = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in tem_var]
        
        # print("tem_var============ ",tem_var)
        yield tem_var

  


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


