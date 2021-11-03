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
    locator_domain = "https://sobiks.com"
    page_url = "https://sobiks.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div/following-sibling::section")

    for d in div:
        location_name = "".join(d.xpath(".//p[./a]/text()[1]"))
        street_address = "".join(d.xpath(".//p[./a]/text()[2]"))
        ad = "".join(d.xpath(".//p[./a]/text()[3]"))
        if location_name.find("Sobik’s of Leesburg") != -1:
            street_address = "".join(
                d.xpath('.//p[./a]/span[@class="LrzXr"]/text()[1]')
            )
            ad = "".join(d.xpath('.//p[./a]/span[@class="LrzXr"]/text()[2]'))

        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        country_code = "US"
        postal = ad.split(",")[1].split()[1].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//p[contains(text(), "Mon")]/text()'))
            .replace("\n", "")
            .strip()
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        if phone.find("ext") != -1:
            phone = phone.split("ext")[0].strip()

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
