import re
import csv
from bs4 import BeautifulSoup

from sgrequests import SgRequests


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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    session = SgRequests()

    start_url = "https://www.carltonbates.com/resources/branch-locator"
    r = session.get(start_url)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    main = soup.find("div", {"id": "cmsContent"}).find_all(
        "div", {"class": "col three"}
    )
    del main[0]
    for dt in main:
        name = ""
        for val in dt.find_all("p", recursive=False):
            if val.find("strong") is not None:
                name = val.find("strong").text
            loc_address = list(val.find("span").stripped_strings)
            loc_lat = val.find("a", text="Map Location")["href"].split("@")
            if len(loc_lat) == 1:
                lat = "<MISSING>"
                lng = "<MISSING>"
            else:
                lat = loc_lat[1].split(",")[0]
                lng = loc_lat[1].split(",")[1]
            ct = loc_address[1].split(",")
            if len(ct) == 2:
                city = ct[0].strip()
                state = ct[1].strip().split(" ")[-2].strip()
                zip = ct[1].strip().split(" ")[-1].strip()
            else:
                st = loc_address[1].split(" ")
                zip = st[-1].strip()
                del st[-1]
                state = st[-1].strip()
                del st[-1]
                city = " ".join(st).strip()
            store = []
            store.append("https://www.carltonbates.com")
            store.append(name.strip())
            store.append(loc_address[0])
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            if re.search("Phone", loc_address[2]):
                store.append(loc_address[2].replace("Phone:", "").strip())
            else:
                store.append("<MISSING>")
            store.append("Carltonbates")
            store.append(lat)
            store.append(lng)
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
