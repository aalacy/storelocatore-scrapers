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
    locator_domain = "https://www.sirspeedy.com/"
    api_url = "https://www.sirspeedy.com/find-locator/#all_locations"

    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@id="locations_columns"]//li/a')

    for b in block:
        page_url = "".join(b.xpath(".//@href"))
        page_url = f"https://www.sirspeedy.com{page_url}"
        if page_url.find("middleburyct420/") != -1:
            continue
        if page_url.find("https://www.sirspeedy.com/bostonma460/") != -1:
            continue
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)

        street_address = (
            "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
            .replace("\n", "")
            .strip()
        )
        city = (
            "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        line = (
            "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
            .replace("\n", "")
            .strip()
        )
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        location_name = (
            "".join(tree.xpath('//p[@itemprop="name"]/text()'))
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(tree.xpath('//span[@itemprop="telephone"]/text()'))
            .replace("\n", "")
            .strip()
        )
        latitude = (
            "".join(
                tree.xpath(
                    '//input[@id="ctl00_cphMainContent_uxLocations_hiddenCenterLat"]/@value'
                )
            )
            .replace("\n", "")
            .strip()
        )
        longitude = (
            "".join(
                tree.xpath(
                    '//input[@id="ctl00_cphMainContent_uxLocations_hiddenCenterLong"]/@value'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(tree.xpath('//p[@class="store_hours"]/text()'))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Email") != -1:
            hours_of_operation = hours_of_operation.split("Email")[0].strip()
        if hours_of_operation.find("Weekends") != -1:
            hours_of_operation = hours_of_operation.split("Weekends")[0].strip()
        if hours_of_operation.find("BY APPT ONLY") != -1:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("(subject to change)") != -1:
            hours_of_operation = hours_of_operation.split("(subject to change)")[
                0
            ].strip()
        if hours_of_operation.find("By") != -1:
            hours_of_operation = hours_of_operation.split("By")[0].strip()
        if hours_of_operation.find("This") != -1:
            hours_of_operation = hours_of_operation.split("This")[0].strip()
        if hours_of_operation.find("Available") != -1:
            hours_of_operation = hours_of_operation.split("Available")[0].strip()

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
