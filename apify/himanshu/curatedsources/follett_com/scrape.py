import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    base_url = "https://www.follett.com"
    r = session.get("https://www.follett.com/college-bookstores/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for link in soup.find_all("div",{"class":"block-store col-lg-4 col-md-4 col-sm-6 col-xs-12 widget-block"}):
        if "http://www.skyo.com/" in link.find_all("a")[-1]['href']:
            continue
        page_url = base_url+link.find_all("a")[-1]['href']
        # print(page_url)
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        location_name = soup1.find("span",{"itemprop":"name"}).text.strip()
        if soup1.find("span",{"itemprop":"streetAddress"}).text.replace("\r",'').strip() != "":
            street_address = re.sub("\s+"," ",str(soup1.find("span",{"itemprop":"streetAddress"}).text.replace("\r",'').strip()))
        else:
            street_address = list(soup1.find("div",{"itemprop":"address"}).stripped_strings)[0].replace("\r",'').strip()
        city = soup1.find("span",{"itemprop":"addressLocality"}).text.strip()
        state = soup1.find("span",{"itemprop":"addressRegion"}).text.strip()
        zipp = list(soup1.find("div",{"itemprop":"address"}).stripped_strings)[-1]


        if soup1.find("span",{"itemprop":"telephone"}):
            phone = soup1.find("span",{"itemprop":"telephone"}).text.strip()
        else:
            phone = "<MISSING>"
        if soup1.find("meta",{"itemprop":"latitude"}):
            lat = soup1.find("meta",{"itemprop":"latitude"})["content"]
        else:
            lat = "<MISSING>"
        if soup1.find("meta",{"itemprop":"longitude"}):
            lng = soup1.find("meta",{"itemprop":"longitude"})["content"]
        else:
            lng = "<MISSING>"
        
        store = []
        store.append("https://www.follett.com")
        store.append(location_name)
        store.append(street_address if street_address else "<MISSING>")
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US" if zipp.replace("-","").replace(" ","").isdigit() else "CA")
        store.append(page_url.split("storeid=")[1].split("-")[-1])
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print("data ==="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~```````````")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
