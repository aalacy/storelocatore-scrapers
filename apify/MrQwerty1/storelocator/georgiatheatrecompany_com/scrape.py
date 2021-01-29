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
    locator_domain = "https://www.gtcmovies.com/"
    api_url = "https://www.gtcmovies.com/theatres"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'pc.cinemas =')]/text()"))
    text = text.split("pc.cinemas =")[1].split(";")[0]
    js = json.loads(text)

    for j in js:
        street_address = (
            f"{j.get('Address1')} {j.get('Address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("City") or "<MISSING>"
        state = j.get("StateCode") or "<MISSING>"
        postal = j.get("ZipCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("CinemaId") or "<MISSING>"
        slug = j.get("TheaterInfoUrl")
        page_url = f"{locator_domain}{slug}"
        location_name = j.get("DisplayName") or "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    f"//div[@class='cinemaItem' and .//a[contains(@href, '{slug[:-1]}')]]//div[./img[contains(@src, 'phone-icon')]]/text()"
                )
            ).strip()
            or "<MISSING>"
        )
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
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
