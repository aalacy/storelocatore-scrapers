import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bell_ca")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "Accept": "text/html, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,gu;q=0.8",
        "Connection": "keep-alive",
        "Host": "bellca.know-where.com",
        "Origin": "https://www.bell.ca",
        "Referer": "https://www.bell.ca/Store_Locator",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
    }
    addresses = []
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=25,
        max_search_results=250,
    )

    for x, y in search:
        result_coords = []
        r = session.get(
            "https://bellca.know-where.com/bellca/cgi/selection?lang=en&loadedApiKey=main&ll="
            + str(x)
            + "%2C"
            + str(y)
            + "&stype=ll&async=results&key",
            headers=headers,
        )

        soup = BeautifulSoup(r.text, "html5lib")
        data = soup.find_all("script", {"type": "application/ld+json"})
        hours = soup.find_all("ul", {"class": "rsx-sl-store-list-hours"})
        hours1 = []
        for time in hours:
            hours1.append(
                " ".join(list(time.stripped_strings))
                .replace(" ", "")
                .replace("p.m.", "p.m. ")
                .replace("Closed", "Closed ")
            )
        try:
            lat = (
                r.text.split("poilat")[1]
                .split(",")[0]
                .replace('"', "")
                .replace(":", "")
            )
            lng = (
                r.text.split("poilon")[1]
                .split(",")[0]
                .replace('"', "")
                .replace(":", "")
            )
        except:
            lat = "<MISSING>"
            lng = "<MISSING>"

        for index, i in enumerate(data):
            text = i.text.replace("\n", "").replace("\t", "").replace("\r", "")
            try:
                json_data = json.loads(text)
            except:
                pass
            street_address = json_data["address"]["streetAddress"]
            city = json_data["address"]["addressLocality"]
            state = json_data["address"]["addressRegion"]
            zipp = json_data["address"]["postalCode"]
            location_name = json_data["name"]
            phone = json_data["telephone"]
            result_coords.append((lat, lng))
            if "Bell" in location_name:
                location_type = "Bell store"
            elif "Source" in location_name:
                location_type = "The Source"
            else:
                location_type = "Other retailer"
            store = []
            store.append("https://www.bell.ca")
            store.append(location_name.strip() if location_name else "<MISSING>")
            store.append(street_address.strip() if street_address else "<MISSING>")
            store.append(city.strip() if city else "<MISSING>")
            store.append(state.strip() if state else "<MISSING>")
            store.append(zipp.strip() if zipp else "<MISSING>")
            store.append("CA")
            store.append("<MISSING>")
            store.append(phone.strip() if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append(hours1[index].strip())
            store.append("<MISSING>")
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
fetch_data()
