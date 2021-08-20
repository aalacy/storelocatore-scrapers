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

    locator_domain = "http://www.pandainn.com"
    api_url = "http://www.pandainn.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Get More Details"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/strong/text()"))
        location_type = "<MISSING>"
        ad = "".join(tree.xpath('//div[@class="location-address"]/text()'))
        street_address = ad.split(",")[0].strip()
        phone = "".join(
            tree.xpath('//span[text()="T:"]/following-sibling::a[1]/text()')
        )
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[1].strip()
        store_number = "<MISSING>"
        latitude = (
            "".join(
                tree.xpath(
                    '//script[contains(text(), "var single_location_center_lat")]/text()'
                )
            )
            .split('var single_location_center_lat = "')[1]
            .split('"')[0]
            .strip()
        )
        longitude = (
            "".join(
                tree.xpath(
                    '//script[contains(text(), "var single_location_center_lat")]/text()'
                )
            )
            .split('var single_location_center_lng = "')[1]
            .split('"')[0]
            .strip()
        )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="row location-hours"]/div/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
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
