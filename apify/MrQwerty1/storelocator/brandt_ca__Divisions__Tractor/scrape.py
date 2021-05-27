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
    locator_domain = "https://brandt.ca/Divisions/Tractor/"
    page_url = "https://www.brandt.ca/Divisions/Tractor/Branch-Locator"
    api = "https://www.brandt.ca/rest/customtableitem.Brandt.Dealers?where=DealerType=%27Tractor%27"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Authorization": "Basic cmVzdHVzZXI6ZmFsY29uOTU=",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.brandt.ca/Divisions/Tractor/Branch-Locator",
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//brandt_dealers")

    for d in divs:
        location_name = "".join(d.xpath("./title/text()")).strip()
        street_address = ", ".join(
            d.xpath('./*[contains(local-name(), "address")]/text()')
        ).strip()
        city = "".join(d.xpath("./city/text()")).strip()
        state = "".join(d.xpath("./stateprovince/text()")).strip()
        postal = "".join(d.xpath("./zippostalcode/text()")).strip()
        country_code = "CA"
        store_number = "".join(d.xpath("./itemid/text()")).strip()
        phone = "".join(d.xpath("./phone/text()")).strip() or "<MISSING>"
        latitude = "".join(d.xpath("./latitude/text()")).strip()
        longitude = "".join(d.xpath("./longitude/text()")).strip()
        location_type = "".join(d.xpath("./dealertype/text()")).strip()
        hours_of_operation = (
            "".join(d.xpath("./branchhoursservice/text()")).strip() or "<MISSING>"
        )

        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                "".join(d.xpath("./branchhoursparts/text()"))
                .replace("\n", ", ")
                .replace("\r", "")
                .strip()
                or "<MISSING>"
            )
        if "- SHOP" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("- SHOP")[0].strip()

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
