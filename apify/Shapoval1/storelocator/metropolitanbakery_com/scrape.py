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

    locator_domain = "https://metropolitanbakery.com/"
    page_url = "https://metropolitanbakery.com/pages/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./h2[@class="h3"]]')

    for d in div:

        location_name = "".join(d.xpath('.//h2[@class="h3"]/text()'))
        location_type = "<MISSING>"
        street_address = "".join(d.xpath('.//h3[@class="h4"]/text()'))
        phone = (
            "".join(d.xpath('.//div/p/strong[contains(text(), "-")]/text()'))
            or "<MISSING>"
        )
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        city = "<MISSING>"
        store_number = "<MISSING>"
        ll = "".join(d.xpath('.//a[contains(text(), "View Map")]/@href'))
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if ll:
            latitude = ll.split("ll=")[1].split(",")[0].strip()
            longitude = ll.split("ll=")[1].split(",")[1].split("&")[0].strip()
        hours_of_operation = (
            "".join(d.xpath(".//div/p[1]//text()")).replace("*", "").strip()
        )
        if hours_of_operation.find("Hours") != -1:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("215") != -1:
            hours_of_operation = hours_of_operation.split("215")[0].strip()
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
