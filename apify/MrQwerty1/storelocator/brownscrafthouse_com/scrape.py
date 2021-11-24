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
    locator_domain = "https://www.brownscrafthouse.com/"
    page_url = "https://www.brownscrafthouse.com/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='row sqs-row' and ./div[@class='col sqs-col-6 span-6'] and .//h3]"
    )

    for d in divs:
        location_name = d.xpath(".//h3//text()")[0].strip()
        if "-" in location_name:
            city = location_name.split("-")[1].split(",")[0].strip()
            state = location_name.split("-")[1].split(",")[1].strip()
        else:
            city = location_name.split(",")[0].strip()
            state = location_name.split(",")[1].strip()

        line = d.xpath(".//p//text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line.pop(0)
        if "," in street_address:
            street_address = street_address.split(",")[0].strip()

        phone = line.pop(0)
        postal = "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        for l in line:
            if "open" in l or "work" in l or "Apply" in l or "Brunch" in l:
                continue
            _tmp.append(" ".join(l.split()))

        hours_of_operation = ";".join(_tmp).replace("pm ", "pm;") or "<MISSING>"

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
