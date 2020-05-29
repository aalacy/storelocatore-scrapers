import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
all=[]
def fetch_data():
    # Your scraper here
    page_url=[]
    res=session.get("https://starrwesternwear.com/contact-us")
    soup = BeautifulSoup(res.text, 'html.parser')
    text=re.findall(r'Visit Our Stores in El Paso, Texas(.*)Keep In Touch',soup.find('div', {'class': 'column main'}).text.replace("(show maps from Google Map, a separate map for each address with the info beneath it)",""),re.DOTALL)[0].strip().split('\n')
    for tex in text:

        tex=tex.split("Open")
        tim=tex[-1]
        tex=tex[0]
        p=re.findall(r'(\(\d{3}\)[\- \d]+)',tex)[0].strip()
        tex=tex.replace(p,"")
        street = tex.split(",")[0]
        tex=tex.replace(street,"")
        loc=street.split("Paso")[0]+"Paso"
        street=street.replace(loc,"").strip()
        zip= re.findall(r'(\d{5})',tex)[0]
        tex=tex.replace(zip,"").replace(",","").strip()
        state=tex.split(" ")[-1]
        city=tex.replace(state,"").strip()

        all.append([
            "https://starrwesternwear.com",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            p,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim.strip(),  # timing
            "https://starrwesternwear.com/contact-us"])

    return all

def scrape():
        data = fetch_data()
        write_output(data)

scrape()

fetch_data()