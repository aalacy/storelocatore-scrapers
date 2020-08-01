import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
import time
from selenium.webdriver.support.wait import WebDriverWait

session = SgRequests()




def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://bakersribs.com"
    addresses = []
    driver = SgSelenium().firefox()
    driver.get("http://bakersribs.com/#locations")
    soup = BeautifulSoup(driver.page_source, "lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"et_pb_blurb_container"}):
        len1 = list(location.stripped_strings)
        if len(len1)!= 1:
            city = location.find("h4").text.replace("Caddo Mills","Greenville") 
            name =location.find("h4").text.strip()
            state =''
            hours1 =''
            phone =''
            st1 = len1[1].replace(", MN Phone:",'')
            state1 = location.text.split("Phone:")[0].replace("\n","").split(",")
            if len(state1)==2:
                state = state1[-1]
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(location.text))
            if phone_list:
                phone =  phone_list[-1]
            hours = list(location.stripped_strings)[2:]
            for q in range(len(hours)):
                if "HOURS" ==hours[q]:
                    hours1 = hours[q+1:]
            # print(hours)
            store = []
            store.append("http://bakersribs.com")
            store.append(name)
            store.append(st1.encode('ascii', 'ignore').decode('ascii').strip().replace(", TX",""))
            store.append(city.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(state.encode('ascii', 'ignore').decode('ascii').strip() if state else "<MISSING>")
            store.append("<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone.replace("\xa0","").encode('ascii', 'ignore').decode('ascii').strip())
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(" ".join(hours1).encode('ascii', 'ignore').decode('ascii').strip())
            store.append("<MISSING>")
            yield store
            # return_main_object.append(store)
            # print("-----------------------",store)
    # return return_main_object


        # print(phone_list)

        # print(list(location.stripped_strings)[0] )
        # print(list(location.stripped_strings))
        # .find_all("a")
    #     location_request = session.get(location["href"],headers=headers)
    #     location_soup = BeautifulSoup(location_request.text,"lxml")
    #     location_details = list(location_soup.find("div",{'class':"et_pb_blurb_description"}).stripped_strings)
    #     geo_request = session.get(location_soup.find("iframe",{'src':re.compile("google")})["src"],headers=headers)
    #     geo_soup = BeautifulSoup(geo_request.text,"lxml")
    #     for script in geo_soup.find_all("script"):
    #         if "initEmbed" in script.text:
    #             geo_data = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
    #             lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
    #             lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
    #     for i in range(len(location_details)):
    #         if "Phone:" == location_details[i]:
    #             phone = location_details[i+1]
    #         elif "Phone:" in location_details[i]:
    #             phone = location_details[i].split("Phone:")[1]
    #     for i in range(len(location_details)):
    #         if "HOURS" == location_details[i]:
    #             hours = " ".join(location_details[i+1:])
    #     store = []
    #     store.append("http://bakersribs.com")
    #     store.append(location.text)
    #     store.append(geo_data.split(",")[1])
    #     store.append(geo_data.split(",")[2])
    #     store.append(geo_data.split(",")[-1].split(" ")[-2])
    #     store.append(geo_data.split(",")[-1].split(" ")[-1])
    #     store.append("US")
    #     store.append("<MISSING>")
    #     store.append(phone.replace("\xa0",""))
    #     store.append("baker's ribs")
    #     store.append(lat)
    #     store.append(lng)
    #     store.append(hours)
    #     return_main_object.append(store)
    # return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
