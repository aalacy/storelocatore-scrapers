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
    locator_domain = "https://www.tjhughes.co.uk/"
    api_url = "https://www.tjhughes.co.uk/map"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(),' function initialize() {')]/text()")
    )
    text = text.split("_marker_latlng =")[1:]
    for t in text:
        source = (
            t.split("_content = ")[1].split("';")[0].replace("'", "").replace("+", "")
        )
        root = html.fromstring(source)

        location_name = "".join(root.xpath("./strong/text()")).strip()
        street_address = (
            ", ".join(root.xpath("//span[contains(@class, 'branch-address')]/text()"))
            .replace("TJ Hughes,", "")
            .strip()
        )
        city = "".join(
            root.xpath("//span[contains(@class, 'branch-city')]/text()")
        ).strip()
        state = "<MISSING>"
        postal = "".join(
            root.xpath("//span[contains(@class, 'branch-postcode')]/text()")
        ).strip()
        country_code = "GB"
        phone = (
            "".join(root.xpath("//span[@class='branch-telephone']/text()"))
            .replace("Tel:", "")
            .strip()
        )
        d = tree.xpath(
            f"//div[@class='store-locator__store' and .//*[contains(@href, '{phone.replace(' ', '')}')]]"
        )[0]
        page_url = "https://www.tjhughes.co.uk" + "".join(
            d.xpath(".//a[@class='store-locator__store__link button']/@href")
        )
        store_number = page_url.split("/")[-1]
        latitude, longitude = eval(t.split("LatLng")[1].split(";")[0])
        location_type = "<MISSING>"
        hours_of_operation = (
            ";".join(d.xpath(".//p[@class='MsoNormal']/text()")[:7]) or "<MISSING>"
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
