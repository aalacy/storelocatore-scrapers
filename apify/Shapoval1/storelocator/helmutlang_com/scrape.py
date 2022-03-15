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

    locator_domain = "https://www.helmutlang.com"
    api_url = (
        "https://www.helmutlang.com/store-locations/store-locations.html?format=ajax"
    )

    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[contains(text(), "HELMUT LANG")]')
    for d in div:
        page_url = "https://www.helmutlang.com/help/?pgid=Stores"
        location_name = "".join(d.xpath(".//text()")).capitalize()

        location_type = "<MISSING>"
        street_address = "".join(
            d.xpath(".//following-sibling::p[1]/text()")
        ).capitalize()
        phone = (
            "".join(d.xpath(".//following-sibling::p[3]/text()"))
            .replace("TEL:", "")
            .strip()
        )
        ad = "".join(d.xpath(".//following-sibling::p[2]/text()"))
        city = ad.split(",")[0].strip().capitalize()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        state = ad.split(",")[1].split()[0].strip()
        if ad.find("TOKYO") != -1:
            state = ad.split(",")[1].strip()
            postal = "<MISSING>"
            country_code = ad.split(",")[-1].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(
                d.xpath('.//following-sibling::p[contains(text(), "MON")][1]/text()')
            )
            .replace("\r\n", "")
            .strip()
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
