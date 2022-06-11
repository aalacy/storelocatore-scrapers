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

    locator_domain = "https://www.savonstores.com"
    page_url = "https://www.savonstores.com/location.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var locations")]/text()'))
        .split("var locations =")[1]
        .split(";")[0]
    )
    div = eval(div)

    for d in div:
        location_name = "<MISSING>"
        location_type = "<MISSING>"
        ad = d[0]
        ad = html.fromstring(ad)
        street_address = "".join(ad.xpath("//text()[1]"))
        adr = "".join(ad.xpath("//text()[2]"))
        phone = "".join(ad.xpath("//text()[3]"))
        state = adr.split(",")[1].split()[0].strip()
        postal = adr.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = adr.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = d[1]
        longitude = d[2]
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
