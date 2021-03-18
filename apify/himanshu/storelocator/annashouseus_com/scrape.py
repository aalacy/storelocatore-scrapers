import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import lxml.html

session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    base_url = "https://annashouseus.com"
    r = session.get("https://annashouseus.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    stores_sel = lxml.html.fromstring(r.text)
    location_object = {}
    for location in soup.find_all("div", {"class": "vc-location-content"}):
        location_details = list(location.stripped_strings)
        for i in range(len(location_details)):
            if location_details[i] == "Phone:":
                phone = location_details[i + 1]
                break
        geo_location = location.find_all("iframe")[-1]["src"]
        if len(geo_location.split("!3d")) != 1:
            location_object[location_details[0]] = [
                phone,
                geo_location.split("!3d")[1].split("!")[0],
                geo_location.split("!2d")[1].split("!")[0],
            ]
        else:
            location_object[location_details[0]] = [phone, "<MISSING>", "<MISSING>"]

    hours = stores_sel.xpath(
        '//div[@class="et_pb_row et_pb_row_1"]//div[@class="et_pb_text_inner"]/p'
    )
    for location in soup.find_all("div", {"class": "vc-locationContainer"}):
        location_details = list(location.stripped_strings)
        address = (
            location_details[-1]
            .replace("\r", "")
            .replace("\n", "")
            .replace("\u200e", "")
        )
        hours_of_operation = "<MISSING>"
        for hour in hours:
            if location_details[0] in "".join(hour.xpath("text()")).strip():
                if "open " in "".join(hour.xpath("text()")).strip():
                    hours_of_operation = (
                        "".join(hour.xpath("text()")).strip().split("open ")[1].strip()
                    )
                elif "temporarily closed" in "".join(hour.xpath("text()")).strip():
                    hours_of_operation = "temporarily closed"

        store = []
        store.append(base_url)
        store.append(location_details[0])
        if len(address.split(",")) == 3:
            store.append(address.split(",")[0])
            store.append(address.split(",")[1])
            store.append(address.split(",")[-1].split(" ")[-2])
            store.append(address.split(",")[-1].split(" ")[-1])
        else:
            store.append(address.split(",")[0])
            store.append(" ".join(address.split(",")[1].split(" ")[1:-1]))
            store.append("<MISSING>")
            store.append(address.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_object[location_details[0]][0])
        store.append("<MISSING>")
        store.append(location_object[location_details[0]][1])
        store.append(location_object[location_details[0]][2])
        store.append(
            hours_of_operation.encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        store.append("https://annashouseus.com/locations/")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
