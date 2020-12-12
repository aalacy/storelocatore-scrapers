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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
    }
    url = "https://www.fye.com/"
    api_url = "https://www.fye.com/stores"

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    _div = tree.xpath("//div[@class='c-store-locator__store']")

    for d in _div:
        locator_domain = url
        page_url = api_url
        location_name = "".join(
            d.xpath(
                ".//span[@class='c-store-locator__store-info c-store-locator__store-name']/text()"
            )
        ).strip()
        line = (
            "".join(d.xpath(".//a[contains(@href, 'maps')]/@href"))
            .split("q=")[1]
            .replace("%20", "")
            .replace("FYE,", "")
        )
        street_address = "".join(
            d.xpath(
                ".//span[@class='c-store-locator__store-info c-store-locator__store-line1']/text()"
            )
        ).strip()
        city = line.split(",")[-4]
        state = line.split(",")[-2]
        postal = line.split(",")[-3]
        country_code = line.split(",")[-1]
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel')]/text()")).strip()
            or "<MISSING>"
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        tr = d.xpath(".//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]/text()")).strip()
            time = "".join(t.xpath("./td[2]/text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
