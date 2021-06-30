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

    locator_domain = "https://ironcactus.com/"
    api_url = "https://ironcactus.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="ubermenu-nav"]/li[./a/img]/a')
    for d in div:

        page_url = "".join(d.xpath("./@href"))
        location_name = "".join(d.xpath(".//span/text()"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_type = "Restaurant"
        street_address = "".join(
            tree.xpath(
                '//div[@class="location-sidebar mobile-removed"]//h2[contains(text(), "Address")]/following-sibling::div/p[1]/text()[1]'
            )
        )
        ad = (
            "".join(
                tree.xpath(
                    '//div[@class="location-sidebar mobile-removed"]//h2[contains(text(), "Address")]/following-sibling::div/p[1]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )

        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        slug = location_name.split()[1].strip()
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = (
            "".join(tree.xpath(f'//script[contains(text(), "{slug}")]/text()'))
            .split('"latitude": "')[1]
            .split('"')[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath(f'//script[contains(text(), "{slug}")]/text()'))
            .split('"longitude": "')[1]
            .split('"')[0]
            .strip()
        )
        phone = (
            " ".join(
                tree.xpath(
                    '//div[@class="location-sidebar mobile-removed"]//h2[contains(text(), "Address")]/following-sibling::div/p[1]/text()'
                )
            )
            .replace("\n", "")
            .split("Tel:")[1]
            .strip()
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="location-sidebar mobile-removed"]//h2[contains(text(), "Bar Hours")]/following-sibling::div/p//text()'
                )
            )
            .replace("\n", "")
            .replace("1030", "10:30")
            .strip()
        )
        if hours_of_operation.find("Daily") != -1:
            hours_of_operation = hours_of_operation.split("Daily")[0].strip()

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
