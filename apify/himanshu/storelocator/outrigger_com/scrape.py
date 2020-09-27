import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }
    return_main_object = []
    base_url = "https://www.outrigger.com"
    locator_domain = "https://www.outrigger.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "outrigger"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"
    r = session.get(
        "https://www.outrigger.com/hotels-resorts", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for view in soup.find_all('a',class_="promo-cta"):
        page_url = base_url + view['href']
        r1 = session.get(base_url+view['href'],headers = headers)
        soup_r1 = BeautifulSoup(r1.text,'lxml')
        dav= "https://schema.milestoneinternet.com/schema/"
        link = (dav+soup_r1.find("link",{"rel":"canonical"})['href'].split("https://www.")[1]+"/schema.json")
        if "https://www.outrigger.com/hotels-resorts/fiji/castaway-island/castaway-island-fiji" in base_url+view['href']:
            link = "https://schema.milestoneinternet.com/schema/outrigger.com/hotels-resorts/fiji/castaway-island/castaway-island-fiji/schema.json"
        r2 = session.get(link,headers = headers).json()
        for adr in r2:
            if "address" in adr:
                location_name = " ".join(adr['name'])
                phone = adr['telephone'].replace(" Toll-free ",'').replace(" or +1 808 823 1402",'').replace("+1 808 923 071","+1 808 923 0711").replace("+1 808 923 311","+1 808 923 3111").replace("+1 808 922 464","+1 808 922 4646")
                city = adr['address']['addressLocality']
                street_address = adr['address']['streetAddress'].replace("\n",' ').strip()
                zipp = adr['address']['postalCode'].replace("Islands","<MISSING>").replace("of","<MISSING>")
                state = adr['address']['addressRegion']
                if "Fiji" in state or "Phuket" in state or "Koh" in state or "Mauritius" in state or "Republic" in state:
                    continue
                page_url=base_url+view['href']
                if "https://www.outrigger.com/hotels-resorts/hawaii/maui/honua-kai" in page_url:
                    street_address ="130 Kai Malina Parkway"

                if "https://www.outrigger.com/hotels-resorts/hawaii/maui/napili-shores-maui-by-outrigger" in page_url:
                    street_address ="5315 Lower Honoapiilani Road"

                if "https://www.outrigger.com/hotels-resorts/hawaii/maui/the-kapalua-villas" in page_url:
                    street_address ="300 Kapalua Drive"
                
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                store = ["<MISSING>" if x == "" else x for x in store]
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
