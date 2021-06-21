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

    locator_domain = "https://caffeartigiano.com/"

    page_url = "https://caffeartigiano.com/pages/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-card"]')
    for d in div:

        phone = (
            "".join(d.xpath('.//div[@class="location-card__content"]/p[3]/text()[3]'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        location_name = (
            "".join(d.xpath('.//div[@class="location-card__content"]/p[2]//text()'))
            .replace("\n", "")
            .strip()
        )
        location_type = "<MISSING>"
        street_address = "".join(
            d.xpath('.//div[@class="location-card__content"]/p[3]/text()[1]')
        )
        adr = (
            "".join(d.xpath('.//div[@class="location-card__content"]/p[3]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        country_code = "Canada"
        state = adr.split(",")[1].split()[0].strip()
        postal = " ".join(adr.split(",")[1].split()[1:]).strip()
        city = adr.split(",")[0].strip()
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="location-card__content"]/p[4]//text()'))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Holidays") != -1:
            hours_of_operation = hours_of_operation.split("Holidays")[0].strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
