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
    locator_domain = "https://friendlymartinc.com/"

    session = SgRequests()
    r = session.get(locator_domain)
    tree = html.fromstring(r.text)
    counties = tree.xpath(
        "//div[@id='fm_locations']//a[contains(@href,'county-locations')]/@href"
    )
    for page_url in counties:
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        divs = tree.xpath("//div[@class='et_pb_row']")
        for d in divs:
            line = (
                d.xpath(".//div[contains(text(), 'Address:')]/text()")[0]
                .replace("\n", "")
                .replace("Address:", "")
                .strip()
            )
            if line.find("–") != -1:
                street_address = line.split("–")[0].strip()
                line = line.split("–")[1].strip()
            else:
                street_address = line.split(",")[0].strip()
                line = ", ".join(line.split(",")[1:])
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            state = line.split()[0]
            postal = line.split()[1]
            country_code = "US"
            location_name = "".join(
                d.xpath(".//div[@class='et_pb_text_inner']//h2[1]//text()")
            ).strip()
            store_number = location_name.split("#")[1].split("–")[0].strip()
            phone = (
                "".join(d.xpath(".//a[contains(@href, 'tel')]/@href")).replace(
                    "tel:", ""
                )
                or "<MISSING>"
            )
            latitude = (
                "".join(d.xpath(".//div[@data-center-lat]/@data-center-lat"))
                or "<MISSING>"
            )
            longitude = (
                "".join(d.xpath(".//div[@data-center-lng]/@data-center-lng"))
                or "<MISSING>"
            )
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
