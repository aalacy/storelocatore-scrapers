import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

DOMAIN = 'https://mastercuts.com'
MISSING = '<MISSING>'

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
HEADERS = {'User-Agent' : user_agent}

session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data=[]
    all_links=[]
    url = "https://www.signaturestyle.com/salon-directory.html"
    response = session.get(url, headers = HEADERS)

    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a",{"class","btn btn-primary"})
    for link in links:
        if "/locations/pr.html" in link['href']:
            continue
        r1 = session.get("https://www.signaturestyle.com"+link['href'], headers=HEADERS)
        soup1 = BeautifulSoup(r1.text, "lxml")
        locations = soup1.find_all("tr")
        for location in locations:
            if "https" not in location.find("a")['href']:
                page_url = "https://www.signaturestyle.com"+location.find("a")['href']
            else:
                page_url = location.find("a")['href']
            all_links.append(page_url)

    for loc_url in all_links:
        if "mastercuts" not in loc_url:
            continue
        res = session.get(loc_url, headers = HEADERS)
        loc_data = BeautifulSoup(res.content, "html.parser")

        loc_soup = loc_data.find(class_="salondetailspagelocationcomp")
        location_name = loc_data.find('h2').text.strip()
        country = "US"
        hours_of_operation = " ".join(list(loc_soup.find(class_="salon-timings").stripped_strings))
        phone = loc_soup.find(id="sdp-phone").text.strip()
        street_address = loc_soup.find('span', attrs={'itemprop': "streetAddress"}).text.strip()
        city = loc_soup.find('span', attrs={'itemprop': "addressLocality"}).text.strip()
        state = loc_soup.find('span', attrs={'itemprop': "addressRegion"}).text.strip()
        zipcode = loc_soup.find('span', attrs={'itemprop': "postalCode"}).text.strip()
        lat = loc_data.find('meta', attrs={'itemprop': "latitude"})["content"]
        lon = loc_data.find('meta', attrs={'itemprop': "longitude"})["content"]
        store_number = loc_url.split("-")[-1].split(".")[0]
        location_type = "<MISSING>"

        if " " in zipcode:
            country = "CA"
        data.append([DOMAIN, loc_url, location_name, street_address, city, state, zipcode, country, store_number, phone, location_type, lat, lon, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
