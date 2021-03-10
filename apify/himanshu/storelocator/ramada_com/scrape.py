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


def get_soup(location_url, headers):
    try:
        r1 = session.get(location_url, headers=headers, allow_redirects=False)
    except:
        pass
    soup1 = BeautifulSoup(r1.text, "lxml")
    return soup1


def fetch_data():
    addresses = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Connection": "keep-alive",
    }
    base_url = "https://www.wyndhamhotels.com"
    location_url1 = "https://www.wyndhamhotels.com/ramada/locations"
    try:
        r = session.get(location_url1, headers=headers, allow_redirects=False)
    except:
        pass
    soup = BeautifulSoup(r.text, "lxml")
    a = soup.find("div", {"class": "aem-rendered-content"}).find_all(
        "div", {"class": "state-container"}
    )[0:53]
    a.append(
        soup.find_all("div", {"class": "aem-rendered-content"})[-3].find_all(
            "div", {"class": "state-container"}
        )[-1]
    )

    all_links = []
    found = []
    for y in a:
        e = y.find_all("li", {"class": "property"})
        for b in e:
            k = b.find("a")["href"]
            location_url = base_url + k
            all_links.append(location_url)
    all_links.extend(
        [
            "https://www.wyndhamhotels.com/ramada/rockville-maryland/the-rockville-hotel-a-ramada/overview",
            "https://www.wyndhamhotels.com/ramada/whitecourt-alberta/ramada-whitecourt/overview",
        ]
    )

    for location_url in all_links:
        if location_url in found:
            continue
        found.append(location_url)
        soup1 = get_soup(location_url, headers)

        b1 = soup1.find("script", {"type": "application/ld+json"})
        if not b1:
            continue
        b = str(b1).split('ld+json">')[1].split("</script>")[0]
        if b != [] and b is not None:
            h = json.loads(b)
            location_name = h["name"].strip()
            street_address = h["address"]["streetAddress"].strip()
            latitude = h["geo"]["latitude"]
            longitude = h["geo"]["longitude"]
            city = h["address"]["addressLocality"].strip()
            if "postalCode" in h["address"]:
                zipp = h["address"]["postalCode"].strip()
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
            if "united-kingdom" in location_url:
                country_code = "UK"
            if "addressRegion" in h["address"]:
                state = h["address"]["addressRegion"]
            else:
                state = "<MISSING>"
            phone = h["telephone"]
            store = []
            store.append(base_url)
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
            addresses.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
