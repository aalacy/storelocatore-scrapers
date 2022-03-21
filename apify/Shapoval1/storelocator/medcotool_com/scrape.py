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

    locator_domain = "http://www.medcocorp.com"
    page_url = "http://www.medcocorp.com/distribution/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    div = tree.xpath("//p[./strong]")

    for d in div:

        location_name = "".join(d.xpath(".//a/text()"))
        location_type = "<MISSING>"
        street_address = "".join(d.xpath(".//following-sibling::p[1]/text()[1]"))
        if street_address.find("5362") != -1:
            street_address = "5362 Royal Woods Parkway"
        if street_address.find("2143 ") != -1:
            street_address = street_address + "" + "Suite 100"
        ad = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        if ad.find("Suite") != -1:
            ad = (
                "".join(d.xpath(".//following-sibling::p[1]/text()[3]"))
                .replace("\n", "")
                .strip()
            )
        phone = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[3]"))
            .replace("\n", "")
            .replace("TEL", "")
            .strip()
        )
        if phone.find("IL") != -1:
            phone = (
                "".join(d.xpath(".//following-sibling::p[1]/text()[4]"))
                .replace("\n", "")
                .replace("TEL", "")
                .strip()
            )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
