import csv

import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "Connection": "keep-alive",
    }
    base_url = "https://www.wyndhamhotels.com"
    locator_domain = "https://www.wyndhamhotels.com/hojo"
    location_url1 = "https://www.wyndhamhotels.com/hojo/locations"
    try:
        r = session.get(location_url1, headers=headers, allow_redirects=False)
    except:
        pass
    soup = BeautifulSoup(r.text, "lxml")
    a = soup.find("div", {"class": "aem-rendered-content"}).find_all(
        "div", {"class": "state-container"}
    )[0:52]
    for y in a:
        e = y.find_all("li", {"class": "property"})
        for b in e:
            k = b.find("a")["href"]
            location_url = base_url + k
            try:
                r1 = session.get(location_url, headers=headers, allow_redirects=False)
            except:
                pass
            soup1 = BeautifulSoup(r1.text, "lxml")
            b1 = soup1.find("script", {"type": "application/ld+json"})
            if not b1:
                continue
            b = str(b1).split('ld+json">')[1].split("</script>")[0]
            if b != [] and b is not None:
                h = json.loads(b)
                location_name = h["name"]
                street_address = h["address"]["streetAddress"]
                latitude = h["geo"]["latitude"]
                longitude = h["geo"]["longitude"]
                city = h["address"]["addressLocality"]
                if "postalCode" in h["address"]:
                    zipp = h["address"]["postalCode"]
                else:
                    zipp = "<MISSING>"
                ca_zip_list = re.findall(
                    r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}", str(zipp)
                )
                us_zip_list = re.findall(
                    re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp)
                )
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country_code = "CA"
                if us_zip_list:
                    zipp = us_zip_list[-1]
                    country_code = "US"
                if len(zipp) == 6 or len(zipp) == 7:
                    country_code = "CA"
                else:
                    country_code = "US"
                if "addressRegion" in h["address"]:
                    state = h["address"]["addressRegion"]
                else:
                    state = "<MISSING>"
                phone = h["telephone"]
                store = []
                store.append(locator_domain)
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address.strip() if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code)
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append("<MISSING>")
                store.append(location_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                yield store
    location_url = "https://www.wyndhamhotels.com/hojo/san-juan-puerto-rico/howard-johnson-centro-cardiovascular-san-juan/overview"
    try:
        r1 = session.get(location_url, headers=headers, allow_redirects=False)
    except:
        pass
    soup1 = BeautifulSoup(r1.text, "lxml")
    b1 = soup1.find("script", {"type": "application/ld+json"})
    b = str(b1).split('ld+json">')[1].split("</script>")[0]
    if b != [] and b is not None:
        h = json.loads(b)
        location_name = h["name"]
        street_address = h["address"]["streetAddress"]
        latitude = h["geo"]["latitude"]
        longitude = h["geo"]["longitude"]
        city = h["address"]["addressLocality"]
        if "postalCode" in h["address"]:
            zipp = h["address"]["postalCode"]
        else:
            zipp = "<MISSING>"
        ca_zip_list = re.findall(
            r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}", str(zipp)
        )
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))
        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"
        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"
        if len(zipp) == 6 or len(zipp) == 7:
            country_code = "CA"
        else:
            country_code = "US"
        if "addressRegion" in h["address"]:
            state = h["address"]["addressRegion"]
        else:
            state = "<MISSING>"
        phone = h["telephone"]
        store = []
        store.append(locator_domain)
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address.strip() if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append("Puerto Rico")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code)
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append(location_url)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
