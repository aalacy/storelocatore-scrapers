import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("petco_com__unleashed")
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
    base_url = "https://stores.petco.com"
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    }
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "html5lib")
    addressses = []
    state_divs = soup.find_all("div", {"class": "map-list-item-wrap is-single"})
    for i, st_div in enumerate(state_divs, start=1):
        if i == 53:
            break
        st_link = st_div.find("a", {"class": "gaq-link"})["href"]
        req1 = session.get(st_link, headers=headers)
        cities_soup = BeautifulSoup(req1.text, "html5lib")
        ct_divs = cities_soup.find_all("div", {"class": "map-list-item-wrap is-single"})
        try:
            for city in ct_divs:
                if city.find("a", {"class": "gaq-link"}):
                    page_url = city.find("a", {"class": "gaq-link"})["href"]
                    req2 = session.get(page_url, headers=headers)
                    store_soup = BeautifulSoup(req2.text, "html5lib")
                    data = store_soup.find(
                        "script", {"type": "application/ld+json"}
                    ).text
                    json_data = json.loads(data)[0]
                    location_name = json_data["name"]
                    store_number = "<MISSING>"
                    address = store_soup.find("p", {"class": "address"})
                    street = address.find_all("span")[0].text
                    cty = address.find_all("span")[1].text.split(",")[0]
                    st = address.find_all("span")[1].text.split(",")[1].split()[0]
                    zip_code = address.find_all("span")[1].text.split(",")[1].split()[1]
                    phone = store_soup.find(
                        "a", {"class": "phone gaq-link"}
                    ).text.strip()
                    lat_lng = store_soup.find("a", {"class": "directions"})[
                        "href"
                    ].split("=")[-1]
                    latitude = lat_lng.split(",")[0]
                    longitude = lat_lng.split(",")[1]
                    new_link = store_soup.find(
                        "a", {"class": "btn btn-primary full-width store-info gaq-link"}
                    )["href"]
                    req3 = session.get(new_link, headers=headers)
                    last_soup = BeautifulSoup(req3.text, "html5lib")
                    script = last_soup.find(
                        "script", {"type": "application/ld+json"}
                    ).text
                    json_data = json.loads(script)
                    openingHours = json_data[0]["openingHours"]
                    location_type = json_data[0]["@type"]
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street)
                    store.append(cty)
                    store.append(st)
                    store.append(zip_code)
                    if zip_code.isdigit():
                        store.append("US")
                    else:
                        store.append("CA")
                    store.append(store_number)
                    store.append(phone)
                    store.append(location_type)
                    store.append(str(latitude) if latitude else "<MISSING>")
                    store.append(str(longitude) if longitude else "<MISSING>")
                    store.append(openingHours)
                    store.append(new_link)
                    if store[2] in addressses:
                        continue
                    addressses.append(store[2])
                    [
                        str(i)
                        .strip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                        for i in store
                    ]
                    yield store
        except:
            continue


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
