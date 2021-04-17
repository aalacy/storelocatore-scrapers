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


def get_hours(page_url):
    _tmp = []
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    li = tree.xpath("//*[contains(@class, 'time-table__item ')]")
    for l in li:
        day = "".join(l.xpath("./span[1]/text()")).strip()
        time = "".join(l.xpath("./span[2]/text()")).strip()
        _tmp.append(f"{day} {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    session = SgRequests()
    locator_domain = "https://www.randstad.ca"
    api_url = "https://www.randstad.ca/api/branches/get-callback"
    headers = {"Content-Type": "application/json;charset=utf-8"}

    for i in range(1, 1000):
        data = {
            "callback": "@Callbacks/getSearchResults",
            "currentRoute": {
                "path": "/locations/:searchParams*",
                "url": "/locations/",
                "isExact": True,
                "params": {"searchParams": f"?p={i}"},
                "routeName": "our-offices",
            },
            "data": {"language": "en"},
        }
        r = session.post(api_url, headers=headers, data=json.dumps(data))
        js = r.json()["searchResults"]["hits"]["hits"]

        for j in js:
            j = j.get("_source")
            location_name = "".join(j.get("title_office"))
            page_url = f'{locator_domain}{"".join(j.get("url"))}'
            adr = "".join(j.get("address_line1"))
            adr2 = "".join(j.get("address_line2") or [])
            street_address = f"{adr} {adr2}".strip() or "<MISSING>"
            city = "".join(j.get("locality")) or "<MISSING>"
            state = "".join(j.get("administrative_area")) or "<MISSING>"
            postal = "".join(j.get("postal_code")) or "<MISSING>"
            country_code = "CA"
            store_number = page_url.split("_")[1].replace("/", "")
            phone = j.get("field_phone")[0].strip()
            if phone.find("\n") != -1:
                phone = phone.split("\n")[0].strip()
            latitude = j.get("lat")[0]
            longitude = j.get("lng")[0]
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

        if len(js) < 5:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
