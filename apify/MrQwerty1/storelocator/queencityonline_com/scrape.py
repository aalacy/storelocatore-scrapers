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
    coords = []
    locator_domain = "https://www.queencityonline.com/"
    api_url = "https://www.queencityonline.com/stores"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), '.dmxGoogleMaps')]/text()"))
    text = text.split('"markers":')[1].replace(": ,", ': "",').split(",  null")[0] + "]"
    js = json.loads(text)
    for j in js:
        lat = j.get("latitude") or "<MISSING>"
        lng = j.get("longitude") or "<MISSING>"
        coords.append((lat, lng))

    divs = tree.xpath("//div[@id='StoreList']")

    for d in divs:
        location_name = "".join(d.xpath(".//h2//a/text()")).strip()
        slug = "".join(d.xpath(".//h2//a/@href"))
        page_url = f"https://www.queencityonline.com{slug}"
        line = d.xpath(".//div[contains(@class, 'lbm-column width-25')][2]/p/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = page_url.split("/")[-2]
        phone = (
            "".join(
                d.xpath(".//div[contains(@class, 'lbm-column width-25')][3]/p/text()")
            )
            .replace("Phone:", "")
            .strip()
            or "<MISSING>"
        )
        latitude, longitude = coords.pop(0)
        location_type = "<MISSING>"

        hours = d.xpath(
            ".//div[contains(@class, 'lbm-column width-25')][4]/p[1]/text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours).replace("\r\n", ";") or "<MISSING>"

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
