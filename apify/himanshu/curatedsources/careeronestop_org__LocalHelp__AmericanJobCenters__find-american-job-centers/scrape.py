import csv
from bs4 import BeautifulSoup as bs
import re
import json
import time
from sgrequests import SgRequests
session = SgRequests()
import requests
 
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
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
    base_url = "https://www.careeronestop.org"
    region_list = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH",'OK',"OR","PA","RI","SC","SD",'TN',"TX","UT","VT","VA","WA","WV","WI","WY"]
    
    for region in region_list:
        
        location_url = "https://www.careeronestop.org/localhelp/americanjobcenters/find-american-job-centers.aspx?&location="+str(region)+"&radius=100&ct=0&y=0&w=0&e=0&sortcolumns=Location&sortdirections=ASC&curPage=1&pagesize=500"

        try:
            soup = bs(requests.get(location_url,headers=headers).content,'lxml')
        

            for tr in soup.find_all("table")[-1].find("tbody").find_all("tr"):

                page_url = base_url + tr.td.a['href']
                location_name = tr.td.a.text
                
                location_type = tr.td.fieldset.text.replace("programtype","")
                store_number = tr.find_all("td")[1]['id'].replace("locationtd_","").strip()

                tag = list(tr.find_all("td")[-1].stripped_strings)

                phone_list = re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(tag[1]))

                if phone_list:
                    phone = phone_list[-1]
                else:
                    phone = tag[1].replace("1-800-285-WORKS","1-800-285-1155").replace("209-558-WORK (9675)","209-558 (9675)")
                hours = tag[2].replace("Hours:","")

                location_soup = bs(requests.get(page_url, headers=headers).content, "lxml")

                data = json.loads(str(location_soup).split("var locinfo =")[1].split(";")[0].strip())

            
                store=[]
                store.append(base_url)
                store.append(location_name)
                store.append(data['ADDRESS1'])
                store.append(data['CITY'])
                store.append(data['STATE'])
                store.append(data['ZIP'])
                store.append("US")
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(data['LAT'])
                store.append(data['LON'])
                store.append(hours)
                store.append(page_url)
            
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store

        except:
            continue  


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
