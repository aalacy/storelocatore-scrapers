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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "http://www.central-oil.com/"
    page_url = "http://www.central-oil.com/central-station-locations-map.html"
    coords = []

    with SgFirefox() as fox:
        fox.get(page_url)
        time.sleep(10)
        source = fox.page_source
        iframes = fox.find_elements_by_xpath("//iframe[@class='actAsDiv']")
        for iframe in iframes:
            fox.switch_to.frame(iframe)
            root = html.fromstring(fox.page_source)
            coords.append(
                get_coords_from_google_url(
                    "".join(root.xpath("//a[contains(@href, 'll=')]/@href"))
                )
            )
            fox.switch_to.default_content()

    tree = html.fromstring(source)
    divs = tree.xpath(
        "//div[@data-muse-type='txt_frame' and ./p/span[contains(text(), '*')]]"
    )

    for d in divs:
        location_name = "".join(
            d.xpath(".//span[contains(text(), 'Central Station')]/text()")
        ).strip()
        line = d.xpath(".//span[@class='Body-Copy']/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
        country_code = "US"
        store_number = location_name.split()[-1]
        phone = "<MISSING>"
        latitude, longitude = coords.pop(0)
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
