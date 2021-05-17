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

    locator_domain = "https://aroma.us"
    api_url = "https://aroma.us/Locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@id, "branch_title")]')

    for d in div:

        page_url = "https://aroma.us/Locations"
        location_name = "".join(
            d.xpath('.//span[@class="branch-panel-title left"]/text()')
        )
        location_type = "<MISSING>"
        ad = " ".join(d.xpath(".//address/text()")).replace("\n", "").strip()
        street_address = " ".join(ad.split(",")[0].split()[:-1])
        phone = "".join(d.xpath('.//p[@class="phone info-text"]/text()'))
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].split()[-1].strip()
        store_number = "<MISSING>"
        latitude = "".join(
            d.xpath('.//following-sibling::div[1]//div[@class="gMap"]/@data-lat')
        )
        longitude = "".join(
            d.xpath('.//following-sibling::div[1]//div[@class="gMap"]/@data-lng')
        )
        if latitude == longitude:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//p[@class="open-hours info-text"]/text()'))
            .replace("\n", "")
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
