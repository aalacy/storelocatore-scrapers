import csv
import json
from bs4 import BeautifulSoup as bs
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
                "page_url",
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
    base_url = "https://www.specsavers.co.uk"
    res = session.get("https://www.specsavers.co.uk/stores/full-store-list")
    soup = bs(res.text, "lxml")
    store_links = soup.select("div.item-list ul li a")
    data = []
    for store_link in store_links:
        page_url = "https://www.specsavers.co.uk/stores/" + store_link["href"]
        missing_urls = [
            "https://www.specsavers.co.uk/stores/sudburysainsburys-hearing",
            "https://www.specsavers.co.uk/stores/skipton-hearing",
        ]
        if page_url in missing_urls:
            continue
        res1 = session.get(page_url)
        soup = bs(res1.text, "lxml")

        detail_url = soup.select_one("div.js-yext-info")["data-yext-url"]
        res2 = session.get(detail_url)
        store = json.loads(res2.text)
        if len(store["response"].keys()) == 0:
            location_name = soup.select_one("h1.store-header--title").string.replace(
                "\n", ""
            )
            address_detail = soup.select_one("div.store p").text.split("\n\n")
            zip = address_detail.pop().replace("\n", "")
            state = address_detail.pop().replace("\n", "")
            state = state[:-1] if state.endswith(",") else state
            city = address_detail.pop().replace("\n", "")
            city = city[:-1] if city.endswith(",") else city
            street_address = " ".join(address_detail).replace("\n", "").strip()
            street_address = (
                street_address[:-1] if street_address.endswith(",") else street_address
            )
            geo = (
                res1.text.split("var position = ")[1]
                .split(";")[0]
                .replace("{", "")
                .replace("}", "")
                .replace("lat:", "")
                .replace("lng:", "")
                .split(",")
            )
            latitude = geo[0].strip()
            longitude = geo[1].strip()
        else:
            location_name = (
                store["response"]["locationName"]
                if "locationName" in store["response"].keys()
                else "<MISSING>"
            )
            street_address = (
                store["response"]["address"]
                if "address" in store["response"].keys()
                else "<MISSING>"
            )
            street_address += (
                " " + store["response"]["address2"]
                if "address2" in store["response"].keys()
                else ""
            )
            city = (
                store["response"]["city"]
                if "city" in store["response"].keys()
                else "<MISSING>"
            )
            state = (
                store["response"]["state"]
                if "state" in store["response"].keys()
                else "<MISSING>"
            )
            zip = (
                store["response"]["zip"]
                if "zip" in store["response"].keys()
                else "<MISSING>"
            )
            latitude = (
                store["response"]["yextDisplayLat"]
                if "yextDisplayLat" in store["response"].keys()
                else "<MISSING>"
            )
            longitude = (
                store["response"]["yextDisplayLng"]
                if "yextDisplayLng" in store["response"].keys()
                else "<MISSING>"
            )

        phone = soup.select_one("span.contact--store-telephone--text").string
        country_code = (
            store["response"]["countryCode"]
            if "countryCode" in store["response"].keys()
            else "<MISSING>"
        )
        store_number = (
            store["response"]["id"] if "id" in store["response"].keys() else "<MISSING>"
        )

        day_of_week = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        if "hours" in store["response"].keys():
            hours = store["response"]["hours"].split(",")
            hours_of_operation = ""
            for x in hours:
                contents = x.split(":")
                hours_of_operation += (
                    day_of_week[int(contents[0]) - 1]
                    + ": "
                    + contents[1]
                    + ":"
                    + contents[2]
                    + "-"
                    + contents[3]
                    + ":"
                    + contents[4]
                    + " "
                )
            hours_of_operation = hours_of_operation.strip()
        else:
            hours_of_operation = "<MISSING>"
        location_type = "Hearing Centre" if "hearing" in page_url else "Optician"

        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
