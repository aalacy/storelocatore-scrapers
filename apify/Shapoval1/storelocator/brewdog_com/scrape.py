import csv
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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


def get_data():
    rows = []
    locator_domain = "https://www.brewdog.com"
    api_url = "https://www.brewdog.com/uk/bar_pages/bar/locator/view_all/1/"
    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = tree.xpath("//div[@class='bar-listing__results__bar']")
    for b in block:

        address = "".join(
            b.xpath(
                './/div[@class="bar-listing__results__bar__detail md:justify-start md:text-left"]/p/text()'
            )
        )
        a = parse_address(International_Parser(), address)
        country_code = a.country or "<MISSING>"
        location_name = (
            "".join(b.xpath('.//h5[@class="heading heading-5 md:text-left"]/text()'))
            or "<MISSING>"
        )
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = a.city or "<MISSING>"
        if city == "Manchester Manchester":
            city = "Manchester"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        store_number = "<MISSING>"
        phone = (
            "".join(
                b.xpath(
                    ".//div[@class='bar-listing__results__bar__detail md:justify-start']/p/text()"
                )
            )
            or "<MISSING>"
        )
        page_url = "".join(
            b.xpath(
                './/div[@class="bar-listing__results__bar__buttons md:text-left"]/a[@class="button button--tertiary bar-listing__results__bar__buttons__view"]/@href'
            )
        )
        if page_url.find("/bars/uk") == -1 and page_url.find("/bars/usa") == -1:
            continue
        session = SgRequests()
        r = session.get(page_url)
        tres = html.fromstring(r.text)
        text = "".join(tres.xpath('//iframe[@class="bar-detail__map"]/@src'))
        try:
            if text.find("q=") != -1:
                latitude = text.split("q=")[1].split(",")[0]
                longitude = text.split("q=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = tres.xpath('//p[@class="copy text-white"]/text()')
        hours_of_operation = list(filter(None, [n.strip() for n in hours_of_operation]))
        hours_of_operation = "".join(hours_of_operation).replace("\n", " ")
        hours_of_operation = list(filter(None, [n.strip() for n in hours_of_operation]))
        hours_of_operation = (
            "".join(hours_of_operation).replace("AM", " AM ").replace("PM", " PM ")
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

        rows.append(row)
    return rows


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
