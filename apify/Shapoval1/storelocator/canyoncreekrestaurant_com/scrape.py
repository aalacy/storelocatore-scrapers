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

    locator_domain = "https://canyoncreekrestaurant.ca"
    api_url = "https://canyoncreekrestaurant.ca/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "fusion-text")]/p/a[./img]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))

        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        location_type = "Restaurant"
        street_address = "".join(
            tree.xpath(
                '//*[text()="Contact Information"]/following-sibling::p/text()[1]'
            )
        )
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        ad = (
            "".join(
                tree.xpath(
                    '//*[text()="Contact Information"]/following-sibling::p/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = " ".join(ad.split(",")[1].split()[1:]).strip()
        if postal.find(" ") == -1:
            postal = postal + " " + "3W6"
        country_code = "CA"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//*[text()="Contact Information"]/following-sibling::p/text()[3]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(tree.xpath('//p[contains(text(), "Mon ")]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        tmpcls = "".join(
            tree.xpath('//strong[contains(text(), "temporarily closed")]/text()')
        )
        if tmpcls:
            hours_of_operation = "Temporarily closed"
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
