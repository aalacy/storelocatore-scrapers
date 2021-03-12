import csv
import json
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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


@retry(stop=stop_after_attempt(3))
def fetch_location(url, headers, session):
    soup = BeautifulSoup(session.get(url, headers=headers).text, "lxml")

    data = json.loads(
        str(soup.find("script", {"type": "application/ld+json"}))
        .split(">")[1]
        .split("<")[0]
    )

    return data, soup


def fetch_data():
    base_url = "https://www.kroger.com/"

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "cache-control": "max-age=0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
    }

    soup = BeautifulSoup(
        session.get(
            "https://www.kroger.com/storelocator-sitemap.xml", headers=headers
        ).text,
        "lxml",
    )

    for url in soup.find_all("loc")[:-1]:
        page_url = url.text
        data, location_soup = fetch_location(page_url, headers, session)

        location_name = location_soup.find(
            "h1", {"data-qa": "storeDetailsHeader"}
        ).text.strip()

        try:
            street_address = data["address"]["streetAddress"]
            city = data["address"]["addressLocality"]
            state = data["address"]["addressRegion"]
            zipp = data["address"]["postalCode"]
        except:
            raw_address = (
                location_soup.find(class_="StoreAddress-storeAddressGuts")
                .get_text(" ")
                .replace(",", "")
                .replace("8  Rd", "8 Rd")
                .replace(" .", ".")
                .replace("..", ".")
                .split("  ")
            )
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[2].strip()
            zipp = raw_address[3].split("Get")[0].strip()
        country_code = "US"
        store_number = "".join(page_url.split("/")[-2:])
        try:
            phone = data["telephone"]
        except:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        lat = data["geo"]["latitude"]
        lng = data["geo"]["longitude"]
        hours = " ".join(data["openingHours"])

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)

        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
