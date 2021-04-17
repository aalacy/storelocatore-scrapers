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

    locator_domain = "https://dashin.com"
    api_url = "https://dashin.com/locations/bl/all-businesses/?bg=dashin"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="lm-nearby__store"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))

        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(
                tree.xpath('//h1[@class="lm-business-detail__header-title"]/text()')
            )
            .replace("\n", "")
            .strip()
        )

        location_type = "<MISSING>"
        street_address = (
            "".join(
                tree.xpath('//a[@class="business-location-info__detail"]/p/text()[1]')
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath('//a[@class="business-location-info__detail"]/p/text()[2]')
            )
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(
                tree.xpath(
                    '//div[contains(text(), "Phone")]/following-sibling::a[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        ll = (
            "".join(tree.xpath('//meta[@name="geo.position"]/@content'))
            .replace("\n", "")
            .strip()
        )
        latitude = ll.split(";")[0].strip()
        longitude = ll.split(";")[1].strip()
        hours_of_operation = (
            "".join(
                tree.xpath(
                    '//div[contains(text(), "Hours")]/following-sibling::div//text()'
                )
            )
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
