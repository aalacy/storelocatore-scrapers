import csv
from sgrequests import SgRequests
from datetime import datetime
from bs4 import BeautifulSoup
import json


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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
    session = SgRequests()
    base_url = "https://cbna.com"
    r = session.get(base_url + "/locations")
    soup = BeautifulSoup(r.text, "lxml")
    data = json.loads(soup.find("locations")["location-data"])["locations"]

    for current_store in data:
        store = []
        store.append("https://cbna.com")
        store.append(current_store["title"])
        street = current_store["address"]["street1"]
        if not street:
            street = "<MISSING>"
        store.append(street)
        store.append(current_store["address"]["city"])
        store.append(current_store["address"]["state"])
        store.append(current_store["address"]["zip"])
        store.append("US")
        store.append(current_store["id"])
        store.append(
            current_store["branchPhoneNumber"]
            if "branchPhoneNumber" in current_store
            and current_store["branchPhoneNumber"]
            else "<MISSING>"
        )
        store.append("<MISSING>")
        store.append(current_store["address"]["lat"])
        store.append(current_store["address"]["lng"])

        link = current_store["url"]
        hours = ""

        days = {
            "0": "Sun",
            "1": "Mon",
            "2": "Tue",
            "3": "Wed",
            "4": "Thu",
            "5": "Fri",
            "6": "Sat",
        }

        if "branchLobbyHours" in current_store:
            store_hours = current_store["branchLobbyHours"] or []
            for key in store_hours:
                day = days[key]
                if not store_hours[key]["open"]:
                    open_close = "Closed"
                else:
                    open_close = (
                        datetime.strptime(
                            store_hours[key]["open"]["date"].split(" ")[1][0:8],
                            "%H:%M:%S",
                        ).strftime("%I:%M %p")
                        + " - "
                        + datetime.strptime(
                            store_hours[key]["close"]["date"].split(" ")[1][0:8],
                            "%H:%M:%S",
                        ).strftime("%I:%M %p")
                    ).strip()
                hours = (hours + " " + day + " " + open_close).strip()
        elif "notes" in current_store:
            hours = current_store["notes"][0]

        if (
            hours
            == "Sun Closed Mon Closed Tue Closed Wed Closed Thu Closed Fri Closed Sat Closed"
        ):
            hours = "<MISSING>"
        store.append(hours if hours != "" else "<MISSING>")
        store.append(link)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
