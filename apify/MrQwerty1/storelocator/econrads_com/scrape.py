import csv

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


def get_hours(page_url):
    _tmp = []
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='store-hours']/div")

    for d in divs:
        day = "".join(d.xpath("./span[1]/text()")).strip()
        time = "".join(d.xpath("./span[2]/text()")).strip()
        _tmp.append(f"{day} {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "http://econrads.com/"
    api_url = "http://econrads.com/Stores/GetAllMapMarkers"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["result"]

    for j in js:
        street_address = j.get("addressLine1") or "<MISSING>"
        line = j.get("addressCityStateZip")
        postal = line.split(",")[-1]
        line = line.split(",")[0].strip()
        city = " ".join(line.split()[:-1])
        state = line.split()[-1]
        country_code = "US"
        store_number = j.get("retailStoreId") or "<MISSING>"
        page_url = f'http://econrads.com{j.get("detailsUrl")}'
        location_name = j.get("title")
        phone = j.get("phoneNumber") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = get_hours(page_url)

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
