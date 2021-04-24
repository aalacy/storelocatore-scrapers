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

    locator_domain = "https://www.beefjerkyoutlet.com"
    api_url = "https://www.beefjerkyoutlet.com/location-finder"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-content"]')
    s = set()
    for d in div:
        slug = "".join(d.xpath('.//a[@class="btn-yellow"]/@href'))
        page_url = f"{locator_domain}{slug}"

        location_name = "".join(d.xpath(".//h4/text()"))
        location_type = "<MISSING>"
        street_address = "".join(d.xpath('.//span[@class="address-line1"]/text()'))
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        state = (
            "".join(d.xpath('.//span[@class="administrative-area"]/text()'))
            or "<MISSING>"
        )
        postal = "".join(d.xpath('.//span[@class="postal-code"]/text()')) or "<MISSING>"
        country_code = "US"
        city = "".join(d.xpath('.//span[@class="locality"]/text()')) or "<MISSING>"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = d.xpath(
            './/div[@class="paragraph paragraph--type--store-hours paragraph--view-mode--default"]//text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
        if (
            hours_of_operation == "<MISSING>"
            and page_url != "https://www.beefjerkyoutlet.com/node/28"
        ):
            session = SgRequests()
            r = session.get(page_url, headers=headers)

            tree = html.fromstring(r.text)
            hours_of_operation = tree.xpath(
                '//span[contains(text(), "Store Hours")]/following-sibling::div[1]//text()'
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
        hours_of_operation = (
            hours_of_operation.replace("Hours may vary Please call for hours", "")
            .replace(
                "Closed New Years Day, Easter Sunday, Thanksgiving Day, Christmas.", ""
            )
            .replace(
                "For Curbside Orders please call during normal business hours to schedule your Pickup",
                "",
            )
            .strip()
        )
        if hours_of_operation.find("Now Open") != -1:
            hours_of_operation = "<MISSING>"
        hours_of_operation = hours_of_operation.replace("OPEN DAILY!", "").strip()
        if hours_of_operation.find("Temporarily Closed") != -1:
            hours_of_operation = "Temporarily Closed"

        line = page_url
        if (
            line in s
            and line.find("110") == -1
            and line.find("209") == -1
            and line.find("20") == -1
        ):
            continue
        s.add(line)
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
