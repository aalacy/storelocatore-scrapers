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

    locator_domain = "https://sangsters.com"
    api_url = "https://sangsters.com/apps/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./a[text()="More Info"]]')
    for d in div:
        page_url = locator_domain + "".join(d.xpath('.//a[text()="More Info"]/@href'))
        location_name = "".join(d.xpath(".//b/text()"))
        location_type = "<MISSING>"
        street_address = (
            "".join(d.xpath(".//b/following::text()[2]"))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        state = (
            "".join(d.xpath(".//b/following::text()[4]"))
            .replace("\n", "")
            .replace(",", "")
            .split()[0]
            .strip()
        )
        postal = (
            "".join(d.xpath(".//b/following::text()[4]"))
            .replace("\n", "")
            .replace(",", "")
            .split()[1:]
        )
        postal = " ".join(postal)
        country_code = "CA"
        city = (
            "".join(d.xpath(".//b/following::text()[3]"))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        store_number = "<MISSING>"
        phone = (
            "".join(
                d.xpath(
                    './/a[contains(@href, "tel")]/text() | .//b/following::text()[5]'
                )
            ).strip()
            or "<MISSING>"
        )

        info = (
            " ".join(d.xpath(".//following-sibling::div[1]//text()"))
            .replace("\r\n", "")
            .strip()
        )
        if page_url == "https://sangsters.com/pages/sk-saskatoon-the-center":
            page_url = "https://sangsters.com/apps/store-locator/"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            tree.xpath(
                '//strong[text()="Address"]/preceding-sibling::text() | //strong[text()="Address"]/preceding-sibling::*/text()'
            )
            or "<MISSING>"
        )

        if hours_of_operation != "<MISSING>":
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation)
        hours_of_operation = (
            hours_of_operation.replace("Regular Store Hours", "")
            .replace(" ( ) ", " ")
            .strip()
        )
        if "Temporary closed" in info:
            hours_of_operation = "Temporary closed"
        if "Closed" in info:
            hours_of_operation = "Closed"

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
