import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    base_url = "https://www.ems.com/find-a-store"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    soup_ = soup.find_all("script")[2]
    for x in soup_:
        soup_ = str(soup_)
    soup_ = soup_.split('window.App["stores"]=')[1]
    soup_ = soup_.replace("];</script>", "]")
    for i in json.loads(soup_):
        location_name = i["title"]

        city = i["slug"].replace("-climbing-school", "")
        state = i["addressRegion"]
        street_address = (
            re.sub(r"\s+", " ", i["address"])
            .replace(", Hadley MA 01035", "")
            .replace(", North Conway, NH 03860", "")
            .replace(", North Conway, NH 03860", "")
            .replace("Peterborough NH 03458", "")
            .replace(" NY 12946", "")
            .replace(", Warwick RI 02889", "")
            .replace(
                " ".join(
                    [word.capitalize() for word in " ".join(city.split("-")).split(" ")]
                ),
                "",
            )
            .replace(" , MA, 01752", "")
            .replace(state, "")
        )

        zipp = i["addressPostalCode"]
        country_code = i["country"].replace("Un", "US")
        store_number = i["legacyId"]
        phone = i["telephone"]
        location_type = "Eastern Mountain Sports"
        latitude = i["coordinates"]["lat"]
        longitude = i["coordinates"]["lng"]
        page_url = "https://www.ems.com/stores/" + i["slug"].lower()
        if i["communication"] == "Coming Soon!":
            continue
        hours_of_operation = ""
        hour = i["hoursOfOperation"]
        for h in hour:
            hours_of_operation = (
                hours_of_operation
                + " "
                + h["day"]
                + " "
                + h["open"]
                + " - "
                + h["closed"]
            )
        store = []
        if "753 Donald J. Lynch Boulevard Marlborough, MA, 01752" in street_address:
            street_address = "753 Donald J. Lynch Boulevard Marlborough"
        store.append("https://www.ems.com")
        store.append(location_name if location_name else "<Missing>")
        store.append(
            street_address.replace(" , MA, 01752", "").replace(", Freeport ME", "")
            if street_address
            else "<Missing>"
        )
        store.append(city if city else "<Missing>")
        store.append(state if state else "<Missing>")
        store.append(zipp if zipp else "<Missing>")
        store.append(country_code)
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<Missing>")
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
