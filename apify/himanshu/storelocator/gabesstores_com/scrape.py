import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import sgzip


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://www.gabesstores.com"
    addresses = []

    zipcodes = sgzip.for_radius(100)
    for zipcode in zipcodes:
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = "Gabe's"
        latitude = ""
        longitude = ""
        location_url = (
            "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=500&location="
            + zipcode
            + "&limit=50&api_key=56bb34af25f122cb7752babc1c8b9767&v=20181201&resolvePlaceholders=true&entityTypes=location&savedFilterIds=39353311"
        )
        k = session.get(location_url, headers=headers).json()
        for i in k["response"]["entities"]:
            street_address = i["address"]["line1"]
            city = i["address"]["city"]
            state = i["address"]["region"]
            zipp = i["address"]["postalCode"]
            location_name = i["name"]
            if "Gabe's - Closed" in location_name or "Gabe's - CLOSED" in location_name:
                continue
            try:
                phone = i["mainPhone"]
            except:
                phone = "<MISSING>"
            latitude = i["yextDisplayCoordinate"]["latitude"]
            longitude = i["yextDisplayCoordinate"]["longitude"]
            if "landingPageUrl" in i:
                page_url = i["landingPageUrl"]
                k1 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(k1.text, "html.parser")
                time = " ".join(
                    list(soup2.find("tbody", {"class": "hours-body"}).stripped_strings)
                )
            else:
                page_url = "<MISSING>"
            store_number = page_url.split("-")[1]
            store = [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zipp,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                time,
                page_url,
            ]
            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))
                store = [x if x else "<MISSING>" for x in store]
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
