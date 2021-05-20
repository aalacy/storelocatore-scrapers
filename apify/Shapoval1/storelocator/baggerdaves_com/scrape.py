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

    locator_domain = "https://www.baggerdaves.com/"
    api_url = "https://www.baggerdaves.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//ul[@id="menu-main-menu"]//a[./span[contains(text(), "Menus & Locations")]]/following-sibling::ul/li/a'
    )

    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h1[@class="entry-title"]/text()'))
        location_type = "<MISSING>"
        street_address = "".join(
            tree.xpath(
                '//span[@class="nearest-posts-results-single-address"]/text()[1]'
            )
        )
        ad = (
            "".join(
                tree.xpath(
                    '//span[@class="nearest-posts-results-single-address"]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = "".join(
            tree.xpath('//span[@class="nearest-posts-results-single-phone"]/text()')
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        city = ad.split(",")[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath("//div[./p/img]//text()"))
            .replace("\n", "")
            .replace("Grub Hub", "")
            .replace("Door Dash", "")
            .strip()
        )
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
