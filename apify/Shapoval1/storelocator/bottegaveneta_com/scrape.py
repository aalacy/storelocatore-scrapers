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

    locator_domain = "https://www.bottegaveneta.com/"
    countries = ["us", "ca"]
    for c in countries:
        api_url = f"https://www.bottegaveneta.com/en-{c}/storelocator"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        jsblock = (
            "".join(
                tree.xpath('//script[contains(text(), "window.exposedData = ")]/text()')
            )
            .split("window.exposedData = ")[1]
            .split(";")[0]
        )
        js = json.loads(jsblock)
        for j in js["storesData"]["stores"]:
            page_url = j.get("detailsUrl")
            location_name = j.get("name")
            location_type = "<MISSING>"
            street_address = f"{j.get('address1')} {j.get('address2') or ''}".replace(
                "None", ""
            ).strip()
            phone = j.get("phone")
            state = j.get("stateCode")
            postal = j.get("postalCode")
            country_code = "".join(c).upper()
            city = j.get("city")
            store_number = j.get("ID")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            tmp = []
            for d in days:
                days = d
                time = j.get(f"{d}Hours")
                line = f"{days} {time}".replace("NO DATA", "Closed")
                tmp.append(line)
            hours_of_operation = ";".join(tmp) or "<MISSING>"
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "Closed"

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
