import csv
import json
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []

    locator_domain = "https://www.badboy.ca/"

    api_url = "https://www.badboy.ca/find-a-store"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "jsonLocations")]/text()'))
        .split("jsonLocations:")[1]
        .split("imageLocations:")[0]
        .replace('"currentStoreId":"1"},', '"currentStoreId":"1"}')
    )
    js = json.loads(jsblock)
    for j in js["items"]:
        page_url = "".join(
            j.get("attributes").get("store_page_url").get("value")
        ).strip()
        if page_url.find("https") == -1:
            page_url = f"https://www.badboy.ca/{page_url}"
        phone = j.get("phone")
        location_name = j.get("name")
        location_type = "<MISSING>"
        street_address = j.get("address")
        country_code = j.get("country")
        state = j.get("state")
        postal = j.get("zip")
        city = "".join(j.get("city"))
        if city.find("Ottawa") != -1:
            state = "Ontario"
        store_number = j.get("id")
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        hours = j.get("schedule_array")
        tmp = []
        for i in days:
            day = i
            open = (
                "".join(hours.get(i).get("from").get("hours"))
                + ":"
                + "".join(hours.get(i).get("from").get("minutes"))
            )
            close = (
                "".join(hours.get(i).get("to").get("hours"))
                + ":"
                + "".join(hours.get(i).get("to").get("minutes"))
            )
            status = "".join(hours.get(i).get(f"{i}_status"))
            line = f"{day}  {open} - {close}"
            if status == "0":
                line = f"{day} Closed"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
