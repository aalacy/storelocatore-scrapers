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
    locator_domain = "https://www.boloco.com"
    page_url = "https://www.boloco.com/locations/"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h4]")

    for d in div:

        location_name = (
            "".join(d.xpath(".//p[1]//text() | .//p[1]/span//text()"))
            .replace("\n", "")
            .strip()
        )
        street_address = "".join(d.xpath('.//span[@class="address"]/text()'))
        if street_address.find("OPEN") != -1:
            street_address = street_address.split("DELIVERY")[1].strip()
        city = "".join(d.xpath('.//span[@class="town"]/text()')).split(",")[0]
        state = (
            "".join(d.xpath('.//span[@class="town"]/text()')).split(",")[1].split()[0]
        )
        country_code = "US"
        postal = (
            "".join(d.xpath('.//span[@class="town"]/text()')).split(",")[1].split()[1]
        )
        store_number = "<MISSING>"
        page_url = (
            "".join(d.xpath('.//a[contains(text(), "DETAILS")]/@href'))
            or "https://www.boloco.com/locations/"
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        phone = (
            "".join(d.xpath('.//span[@class="phone"]/text()'))
            .replace("\n", "")
            .replace("-----", "")
            .strip()
        )
        if phone.find("Closed") != -1:
            phone = phone.split("Closed")[0]
        hours_of_operation = d.xpath('.//p[.//strong[contains(text(), "Sun")]]//text()')
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation).replace(": -", " Closed")
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
        if page_url != "https://www.boloco.com/locations/":
            session = SgRequests()
            r = session.get(page_url)
            tree = html.fromstring(r.text)
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
