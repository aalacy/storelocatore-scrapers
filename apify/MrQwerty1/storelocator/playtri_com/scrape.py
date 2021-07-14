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
    locator_domain = "https://www.playtri.com/"
    page_url = "https://www.playtri.com/locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[./p[contains(text(), '☎')]]|//div[./h3/strong]")

    js = tree.xpath("//div[@data-block-json]/@data-block-json")
    js_list = []
    for j in js:
        try:
            j = json.loads(j)["location"]
        except:
            continue
        js_list.append(j)

    for d, j in zip(divs, js_list):
        location_name = d.xpath(".//h3//text()")[0].strip()
        street_address = "".join(
            d.xpath(".//h3/following-sibling::p[1]/text()")
        ).strip()
        line = j.get("addressLine2").replace(",", "")
        postal = line.split()[-1]
        state = line.split()[-2]
        city = line.replace(postal, "").replace(state, "").strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//*[contains(text(), '☎')]//text()"))
            .replace("☎", "")
            .strip()
            or "<MISSING>"
        )
        if "jason" in phone:
            phone = phone.split("jason")[0].strip()
        latitude = j.get("markerLat") or "<MISSING>"
        longitude = j.get("markerLng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(
                ";".join(
                    d.xpath(
                        ".//p[./strong[contains(text(), 'Hours')]]/following-sibling::p/text()"
                    )
                ).split()
            )
            or "<MISSING>"
        )

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
