import csv
import requests
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jalexanders_com')


session = SgRequests()
def write_output(data):
	with open('data.csv', mode='w',newline="") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
						 "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)
def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    returnres=[]
    base_url="https://jalexanders.com/locations/"
    r = session.get("https://jalexanders.com/locations/",headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    for link  in soup.find_all("div",{"class":"restaurantCard"}):
        add = list(link.stripped_strings)
        page_url =link.find("a")['href']
        try:
            latitude = link.find("a",{"href":re.compile("https://www.google")})['href'].split("@")[1].split(",")[0]
            lon = link.find("a",{"href":re.compile("https://www.google")})['href'].split("@")[1].split(",")[1]
        except:
            
            if link.find("a",{"href":re.compile("https://www.google")})==None:
                latitude = "<MISSING>"
                lon = "<MISSING>"
            else:
                latitude =link.find("a",{"href":re.compile("https://www.google")})['href'].split("sll=")[1].split(",")[0]
                lon = link.find("a",{"href":re.compile("https://www.google")})['href'].split("sll=")[1].split(",")[1].split("&")[0]
        street_address = add[4]
        h = ''
        for index,i in enumerate(add):
            if i=="Hours of Operation":
                h = add[index+1:]
                add = add[:index-1]
        hour=''  
        phone = add[-1]
        city = add[-2].split(",")[0]
        state = add[-2].split(",")[-1].strip().split()[0]
        zipp = add[-2].split(",")[-1].strip().split()[-1]
        hour = " ".join(h).replace("Dining Room Open",'')
        if add[4:-2]:
            street_address = " ".join(add[4:-2])
        else:
            street_address = add[2]
        location_name = add[0] 
        location_type = add[0].split("|")[0].strip()
        store =[]
        store.append("https://jalexanders.com/")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state.replace("North","North Carolina"))
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(lon if lon else "<MISSING>")
        store.append(hour.replace('Patio Dining Open ','') if hour else "<MISSING>")
        store.append(page_url)
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
