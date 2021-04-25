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


def get_hours(page_url):
    _tmp = []
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    li = tree.xpath(
        "//div[@id='hours1-app-root']//li|//div[@data-widget-name='hours-default']//li"
    )
    for l in li:
        day = "".join(l.xpath("./span[1]//text()")).strip()
        time = "".join(l.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")
        if "Sun" in day:
            break

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://www.germainofcolumbus.com/"
    api_url = "https://www.germainofcolumbus.com/locations/index.htm"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//ol[@id='proximity-dealer-list']/li")

    for d in divs:
        location_name = "".join(d.xpath(".//a[@class='url']/span/text()")).strip()
        page_url = "".join(d.xpath(".//a[@class='url']/@href")) or api_url
        street_address = (
            "".join(d.xpath(".//span[@class='street-address']/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(d.xpath(".//span[@class='locality']/text()")).strip() or "<MISSING>"
        )
        state = (
            "".join(d.xpath(".//span[@class='region']/text()")).strip() or "<MISSING>"
        )
        postal = (
            "".join(d.xpath(".//span[@class='postal-code']/text()")).strip()
            or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        try:
            phone = d.xpath(
                ".//li[@data-click-to-call-phone]/@data-click-to-call-phone"
            )[0].split("?")[0]
        except IndexError:
            phone = "<MISSING>"
        latitude = "".join(d.xpath(".//span[@class='latitude']/text()")) or "<MISSING>"
        longitude = (
            "".join(d.xpath(".//span[@class='longitude']/text()")) or "<MISSING>"
        )
        location_type = "<MISSING>"

        if page_url == api_url:
            hours_of_operation = "<MISSING>"
        else:
            hours_of_operation = get_hours(page_url)

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
