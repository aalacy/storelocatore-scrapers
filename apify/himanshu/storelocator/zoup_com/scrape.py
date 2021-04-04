import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    address = []
    base_url = "https://www.zoup.com"
    r = session.get("https://www.zoup.com/eateries/#location-listing", headers=headers)
    soup = BeautifulSoup(r.text, "html5lib")
    data = soup.find("script", {"type": "text/javascript"})
    json_data = (
        data.text.split("window.locations = ")[1]
        .split("window.states =")[0]
        .replace("}];", "}]")
    )
    final_data = json.loads(json_data)
    for i in final_data:
        data_h = []
        k = i["hours"]
        weekday = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        for (k, j) in zip(k, weekday):
            data_h.append((j + ": " + k["opentime"] + " - " + k["closetime"]))
        data_h1 = " ".join(data_h)
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(i["friendly_name"] if i["friendly_name"] else "<MISSING>")
        store.append(i["address"] if i["address"] else "<MISSING>")
        store.append(i["city"] if i["city"] else "<MISSING>")
        store.append(i["state"] if i["state"] else "<MISSING>")
        store.append(i["zip"] if i["zip"] else "<MISSING>")
        store.append(i["country"] if i["country"] else "<MISSING>")
        store.append(i["storenumber"] if i["storenumber"] else "<MISSING>")
        store.append(i["phone"] if i["phone"] else "<MISSING>")
        store.append("Zoup! Eatery" if "Zoup! Eatery" else "<MISSING>")
        store.append(i["lat"] if i["lat"] else "<MISSING>")
        store.append(i["lng"] if i["lng"] else "<MISSING>")
        store.append(data_h1 if data_h1 else "<MISSING>")
        store.append(
            "https://www.zoup.com" + i["url"]
            if "https://www.zoup.com" + i["url"]
            else "<MISSING>"
        )
        if store[2] in address:
            continue
        address.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
