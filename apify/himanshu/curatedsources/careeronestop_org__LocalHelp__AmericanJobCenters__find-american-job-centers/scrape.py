import csv
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip
import time
from sgrequests import SgRequests
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
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    addressess=[]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    lens1=0
    while zip_code:
        result_coords = []
       # print("remaining zipcodes: " + str(len(search.zipcodes)))
        location_url ="https://www.careeronestop.org/localhelp/americanjobcenters/find-american-job-centers.aspx?&location="+str(zip_code)+"&radius=500&sortcolumns=Distance&sortdirections=ASC&curPage=1&pagesize=500"
        locator_domain = ""
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        page_url = ''
       
        r = session.get(location_url,headers=headers)
        try:
            soup = bs(r.text,'lxml').find("tbody").find_all("tr")
            lens1 = len(soup)

            current_results_len = lens1       # it always need to set total len of record.
            for script in soup:
                try:
                    url = "https://www.careeronestop.org"+script.find("a")['href']
                    page_url = "https://www.careeronestop.org"+script.find("a")['href']
                    # print("~~~~~~~~~~~~  ",url)
                except:
                    pass
                try:
                    r1= session.get(page_url,headers=headers)
                    soup1 = bs(r1.text,'lxml')
                except:
                    pass
                
                try:
                    location_name = soup1.find("div",{"id":"detailsheading"}).text.strip()
                except:
                    pass
                d=''
                try:
                    phone =soup1.find("a",{"href":re.compile("tel")}).text.strip()
                    phone = soup1.find(lambda tag: (tag.name == "b" ) and "Phone" in tag.text.strip()).parent.parent.text.strip().replace("Phone",'').split("or")[0].split("and")[0]
                    if "ext" in phone:
                        phone = "-".join(phone.split("-")[:-1])+phone.split("ext")[-1].replace(".",'')
                except:
                    phone=''
                # tag_add = json.loads(soup1.find(lambda tag: (tag.name == "script" ) and "var locinfo" in tag.text.strip()).text.split("var locinfo =")[1].split("var mapapi")[0].strip()[:-1])
                try:
                    tag_add = (json.loads(str(soup1).split("var locinfo =")[1].split("var")[0].strip()[:-1]))
                except:
                    pass
                try:
                    hours_of_operation = " ".join(list(soup1.find(lambda tag: (tag.name == "td" or tag.name == "h2") and "Hours" in tag.text.strip()).parent.stripped_strings)).replace("Hours",'').strip()
                except:
                    hours_of_operation=''

                store=[]
                store.append("https://www.careeronestop.org")
                store.append(location_name)
                store.append(tag_add['ADDRESS1'])
                store.append(tag_add['CITY'])
                store.append(tag_add['STATE'])
                store.append(tag_add['ZIP'] if tag_add['ZIP'] else "<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(tag_add['LAT'] if tag_add['LAT'] else "<MISSING>")
                store.append(tag_add['LON'] if tag_add['LON'] else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url)
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store
                
        except:
            current_results_len = 0

        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
