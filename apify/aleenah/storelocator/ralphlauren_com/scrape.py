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

    all = []
    url_list = [
        "https://www.ralphlauren.com/findstores?dwfrm_storelocator_country=CA&dwfrm_storelocator_findbycountry=Search&findByValue=CountrySearch",
        "https://www.ralphlauren.com/findstores?dwfrm_storelocator_country=GB&dwfrm_storelocator_findbycountry=Search&findByValue=CountrySearch",
        "https://www.ralphlauren.com/findstores?dwfrm_storelocator_country=US&dwfrm_storelocator_findbycountry=Search&findByValue=CountrySearch"]
    for url in url_list:
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        # print(res.content)
        """sls = soup.find_all('div', {'class': 'store-listing-storediv'})

        for s in sls:
            page_url.append("https://www.ralphlauren.com/"+s.find('a').get('href'))"""

        data = soup.find_all('script', {'type': 'application/ld+json'})[3].text
        locs = re.findall(r'"legalName":"([^"]*)"', data)
        print("locs ", len(locs))
        timing = re.findall(r'"openingHours":"([^"]+)"', data)
        streets = re.findall(r'"streetAddress":"([^"]+)"', data)
        countries = re.findall(r'"addressCountry":"([^"]+)"', data)
        states = re.findall(r'"addressRegion":"([^"]+)"', data)
        if states == []:
            states = re.findall(r'"Location":"([^"]+)"', data)
        cities = re.findall(r'"areaServed":"([^"]+)"', data)
        phones = re.findall(r'"telephone":"([^"]+)"', data)
        print("street ", len(streets))

        urls = soup.find_all('span', {'class': 'store-listing-name'})
        data = soup.find('div', {'class': 'storeJSON hide'}).get('data-storejson')
        # print(data)
        if data != "null":
            js = json.loads("".join(data))
            for j in js:
                city = cities[js.index(j)]
                state = states[js.index(j)]
                country = countries[js.index(j)]
                lat = j["latitude"]
                lon = j["longitude"]
                # zip = j["postalCode"]
                phone = phones[js.index(j)]
                # print(urls[js.index(j)].find('a').get('href'))
                id = re.findall(r'StoreID=([\d]+)_', urls[js.index(j)].find('a').get('href'))[0]
                loc = locs[js.index(j)]
                if loc.strip() == "":
                    loc = "<MISSING>"
                tim = timing[js.index(j)].replace("\n", " ").replace("<br>", "").replace("<br/>", "").replace("\\n", " ").replace("<br/", "").replace("<BR>", "")
                sz = streets[js.index(j)].replace("\n", " ").split(",")
                zip = sz[-1].strip()
                del sz[-1]
                street = " ".join(sz)

                all.append([
                    "https://www.ralphlauren.com",
                    loc,
                    street.replace("\n"," "),
                    city,
                    state,
                    zip,
                    country,
                    id,  # store #
                    phone,  # phone
                    "<MISSING>",  # type
                    lat,  # lat
                    lon,  # long
                    tim.strip(),  # timing
                    url])
        else:
            print("null")
            for i in range(len(locs)):
                tim = timing[i].replace("\n", " ").replace("<br/>", "").replace("<br>", "").replace("\\n", " ").replace("<br/", "").replace("<BR>", "")
                sz = streets[i].replace("\n", " ").split(",")

                zip = sz[-1].strip()
                del sz[-1]
                street = " ".join(sz)
                id = re.findall(r'StoreID=([\d]+)_', urls[js.index(j)].find('a').get('href'))[0]
                loc=locs[i]
                if loc.strip() == "":
                    loc = "<MISSING>"
                all.append([
                    "https://www.ralphlauren.com",
                    loc,
                    street.replace("\n"," "),
                    cities[i],
                    states[i],
                    zip,
                    countries[i],
                    id,  # store #
                    phones[i],  # phone
                    "<MISSING>",  # type
                    "<INACCESSIBLE>",  # lat
                    "<INACCESSIBLE>",  # long
                    tim.strip().replace("Mon:"," Mon:").replace("Tue:"," Tue:").replace("Wed:"," Wed:").replace("Thu:"," Thu:").replace("Fri:"," Fri:").replace("Sat:"," Sat:").replace("Sun:"," Sun:").replace("  "," "),  # timing
                    url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

