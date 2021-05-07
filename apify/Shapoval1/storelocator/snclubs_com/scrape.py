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

    locator_domain = "https://fitnessworld.ca"
    api_url = "https://fitnessworld.ca/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(@class, "now-open")]')

    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        location_name = (
            "".join(d.xpath('.//div[@class="location-name"]/text()'))
            .replace("\n", "")
            .strip()
        )

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_type = "<MISSING>"
        street_address = (
            "".join(tree.xpath('//span[@itemprop="address"]/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        adr = (
            "".join(tree.xpath('//span[@itemprop="address"]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        adr = adr.replace(",", "").replace("BC", ",BC").replace("Canada", "")

        phone = "".join(tree.xpath('//div[@itemprop="telephone"]/a/text()')).strip()
        state = adr.split(",")[1].split()[0].strip()
        postal = " ".join(adr.split(",")[1].split()[1:]).strip() or "<MISSING>"
        country_code = "Canada"
        city = adr.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "".join(tree.xpath('//div[@class="marker"]/@data-lat'))
        longitude = "".join(tree.xpath('//div[@class="marker"]/@data-lng'))
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="hours"]/div/span/text()'))
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
