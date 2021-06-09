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


def fetch_data():
    out = []
    locator_domain = "https://kristoil.com/"
    page_url = "https://kristoil.com/locations/"
    api_url = "https://kristoil.com/wp-content/themes/krist-2020/ajax/map.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://kristoil.com/locations/",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json().values()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    for j in js:
        location_name = j.get("title")
        store_number = j.get("ID")
        phone = j.get("phone") or "<MISSING>"
        _id = phone[-4:]
        a = j.get("location")

        li = tree.xpath(
            f"//li[@class='grid grid--locations grid--one-col-mobile locations-list__list-item' and .//a[contains(text(), '-{_id}')]]"
        )[0]
        city = "".join(li.xpath("./text()")).replace(".", "").strip()
        line = (
            "".join(
                li.xpath(
                    ".//li[@class='locations-list__phone-number']/preceding-sibling::li[1]/text()"
                )
            )
            .replace(".", "")
            .strip()
        )
        street_address = line.rsplit(city, 1)[0].replace(",", "").strip()
        sz = line.rsplit(city, 1)[-1].replace(",", "").strip()
        state = sz.split()[0]
        postal = sz.replace(state, "") or "<MISSING>"
        country_code = "US"
        latitude = a.get("lat") or "<MISSING>"
        longitude = a.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
