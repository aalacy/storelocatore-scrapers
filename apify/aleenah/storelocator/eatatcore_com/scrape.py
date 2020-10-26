import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
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

def fetch_data():
    # Your scraper here

    res=session.get("https://www.corelifeeatery.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    urls = soup.find_all('div', {'class': 'col-md-4 grid-item'})
    all=[]
    for url in urls:
        id = url.find('article').get('id')
        loc = url.find('a').text
        url=url.find('a').get('href')

        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        if "Opening Soon" in soup.find('h1', {'class': 'panel-title'}).text:
            continue
        data = soup.find('script', {'type': 'application/ld+json'}).contents
        js = json.loads("".join(data))
        addr=js["address"]
        timl = js["openingHoursSpecification"]
        tim = ""
        for l in timl:
            tim += ", ".join(l["dayOfWeek"]) + ": " + l["opens"] + " - " + l["closes"] + " "
        coord=soup.find('iframe').get('src')
        long = re.findall(r'!1d[-?\d\.]*!2d([-?\d\.]*)', coord)[0].replace("?", "")
        lat = re.findall(r'!3d(-?[\d\.]*)', coord)[0].replace("?", "")

        p=soup.find('p', {'style': 'text-align: center;'}).text.split("\n")[-1].replace("Phone:","").strip()
        #print(p)
        if p=="":
            p="<MISSING>"

        all.append([
            "https://www.eatatcore.com",
            loc,
            addr["streetAddress"],
            addr["addressLocality"],
            addr["addressRegion"],
            addr["postalCode"].split("-")[0],
            addr["addressCountry"],
            id.replace("post-",""),  # store #
            p,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim.strip(),  # timing
            url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
