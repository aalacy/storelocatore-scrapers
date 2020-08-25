import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    address = []
    address_main = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.americafirst.com/"
    db =  'https://www.americafirst.com/content/afcu/en/about/branch-search-results/_jcr_content/main/branch_search_result.nocache.html'
    r = session.get(db, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data_8 = (soup.find_all("div",{"class":"h4"}))
    for i in data_8 :
        location_name = i.text.strip()
        # print(location_name)
        data = (i.text.strip().replace(" ","-").lower().replace("'","").replace(".","").replace("12th-st","12th-street").replace("park-city,-the-market-at-park-city","the-market-at-park-city").replace("boise-office","boise"))
        link = ("https://www.americafirst.com/content/afcu/en/about/branches/"+str(data)+"-branch/_jcr_content/main/column_container_add/col-1/branch-details-info.nocache.html").replace("12th-st","12th-street").replace("park-city,-the-market-at-park-city","the-market-at-park-city").replace("boise-office","boise")
        #print(link)
        r1 = session.get(link, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        data_9 = (soup1.find_all("div",{"class":"col-12 col-sm-12 col-xl-12 col-lg-12 col-md-6"}))
        try:
            for k in data_9:
                data_new = k.find("div",{"class":"branch-address"})
                data_add = ((data_new.text.strip().replace("\n","").lstrip().rstrip().split("  ")[0].split("\t\t\t")))
                data_new_1 = (k.find("div",{"class":"btn-afcu-top"}))
                data_add_1 = (data_new_1.find("a")['href'])
                hours = (k.find("div",{"class":"branch-hours"}))
                hours_of_operation = (hours.text.replace("\n"," ").replace("\t"," ").replace("     "," ").strip())
                url_data = "https://www.americafirst.com/about/branches/"+str(data)+"-branch.html"
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(data_add[1])
                store.append(data_add[-1].split(",")[0].strip())
                store.append(data_add[-1].split(",")[1].strip().split(" ")[0])
                store.append(data_add[-1].split(",")[1].strip().split(" ")[1])
                store.append("US")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("America First")
                store.append(data_add_1.split("=")[1].split(",")[0])
                store.append(data_add_1.split("=")[1].split(",")[1])
                store.append(hours_of_operation)
                store.append(url_data)
                
                yield store
        except:
            pass
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
