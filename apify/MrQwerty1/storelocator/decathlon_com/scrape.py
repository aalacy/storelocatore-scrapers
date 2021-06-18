import csv
import time

from lxml import html
from sgselenium import SgFirefox


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


def get_data(source):
    locator_domain = "https://www.decathlon.com/"
    tree = html.fromstring(source)

    location_name = "".join(tree.xpath("//title/text()")).split("|")[0].strip()
    page_url = "".join(tree.xpath("//link[@rel='alternate']/@href"))
    line = tree.xpath(
        "//div[./div/h4[contains(text(), 'Location')]]/following-sibling::div[1]//text()"
    )
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//div[./div/h4[contains(text(), 'Contact')]]/following-sibling::div[1]//text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude = (
        "".join(tree.xpath("//div[@data-latitude]/@data-latitude")) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//div[@data-longitude]/@data-longitude")) or "<MISSING>"
    )
    location_type = "<MISSING>"

    hours = tree.xpath(
        "//div[./div/h4[contains(text(), 'Hours')]]/following-sibling::div[1]//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours) or "<MISSING>"

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

    return row


def fetch_data():
    out = []
    with SgFirefox() as fox:
        fox.get("https://www.decathlon.com/pages/store-finder")
        time.sleep(10)
        for i in range(100):
            divs = fox.find_elements_by_xpath("//span[text()='Info']")
            d = divs[i]
            d.click()
            time.sleep(10)
            source = fox.page_source
            row = get_data(source)
            out.append(row)
            if i == len(divs) - 1:
                break
            fox.back()
            time.sleep(10)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
