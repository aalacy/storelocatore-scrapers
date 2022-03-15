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
    session = SgRequests()
    locator_domain = "https://www.farmershomefurniture.com"
    api_url = "https://secure.gotwww.com/gotlocations.com/microd/farmershomefurniture.com/index.php?bypass=y"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Referer": "https://secure.gotwww.com/gotlocations.com/microd/farmershomefurniture.com/responsive.wap.getloc.php?brand=",
        "Upgrade-Insecure-Requests": "1",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    script = "".join(tree.xpath("//script[contains(text(),'L.marker')]/text()"))

    for line in script.split("\n"):
        if line.find("L.marker") == -1:
            continue

        root = html.fromstring(line.split("'")[1])
        location_name = (
            "".join(root.xpath(".//span[@class='name']//a/text()")).strip()
            or "<MISSING>"
        )
        if location_name == "name":
            continue
        page_url = "".join(root.xpath(".//span[@class='name']//a/@href"))
        street_address = (
            "".join(root.xpath(".//span[@class='address']/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(root.xpath(".//span[@class='city']/text()"))
            .replace(",", "")
            .strip()
            or "<MISSING>"
        )
        state = (
            "".join(root.xpath(".//span[@class='state']/text()")).strip() or "<MISSING>"
        )
        postal = (
            "".join(root.xpath(".//span[@class='zip']/text()")).strip() or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(root.xpath("//a[contains(@href, 'tel')]/text()")).strip()
            or "<MISSING>"
        )
        latitude = line.split("[")[1].split(",")[0] or "<MISSING>"
        longitude = line.split("]")[0].split(",")[-1] or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(root.xpath(".//span[@class='hours']/text()"))
            .replace("hours:", "")
            .strip()
            or "<INACCESSIBLE>"
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
