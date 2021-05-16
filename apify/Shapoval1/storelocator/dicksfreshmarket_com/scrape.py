import csv
import time
from lxml import html
from sgselenium import SgFirefox


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    locator_domain = "https://dicksfreshmarket.com/contact"
    all_store_data = []
    with SgFirefox() as fox:
        fox.get(locator_domain)
        time.sleep(5)
        all = fox.find_elements_by_xpath('//div[contains(@class, "fade tab-pane")]')
        for l in all:
            a = l.get_attribute("innerHTML")
            tree = html.fromstring(a)
            div = tree.xpath('//div[@class="row"]')
            for d in div:
                location_name = "".join(d.xpath(".//h2/text()"))
                street_address = "".join(d.xpath(".//p[1]/text()"))
                ad = "".join(d.xpath(".//p[2]/text()"))
                city = ad.split(",")[0].strip()
                state = ad.split(",")[1].split()[0].strip()
                zip_code = ad.split(",")[1].split()[1].strip()
                phone_number = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
                hours = "".join(
                    d.xpath(
                        './/b[contains(text(), "HOURS:")]/following-sibling::text()'
                    )
                )
                store_number = "<MISSING>"
                location_type = "Dick's Fresh Market"
                lat = "".join(d.xpath(".//iframe/@src")).split("q=")[1].split(",")[0]
                longit = (
                    "".join(d.xpath(".//iframe/@src"))
                    .split("q=")[1]
                    .split(",")[1]
                    .split("&")[0]
                )
                page_url = "https://dicksfreshmarket.com/contact"
                country_code = "US"

                store_data = [
                    locator_domain,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country_code,
                    store_number,
                    phone_number,
                    location_type,
                    lat,
                    longit,
                    hours,
                    page_url,
                ]

                all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
