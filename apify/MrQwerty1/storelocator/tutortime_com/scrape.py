import csv
import re

from lxml import html
from sgselenium import sgselenium
from sgrequests import SgRequests
from sgselenium.sgselenium import Options


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


def get_id(text):
    regex = r"\d{3,4}"
    _id = re.findall(regex, text)
    if _id:
        return _id[0]
    return "<MISSING>"


def get_urls():
    session = SgRequests()
    r = session.get("https://www.tutortime.com/child-care-centers/find-a-school/")
    tree = html.fromstring(r.text)

    return tree.xpath("//map[@id='USMap']/area/@href")


def fetch_data():
    out = []
    options = Options()
    options.headless = True
    fox = sgselenium.webdriver.Firefox(options=options)
    locator_domain = "https://www.tutortime.com/"
    location_type = "<MISSING>"
    urls = get_urls()
    for u in urls:
        fox.get(f"https://www.tutortime.com{u}")
        tree = html.fromstring(fox.page_source)
        divs = tree.xpath(
            "//div[@class='locationCards thisBrand row']//div[@class='locationCard']"
        )

        for d in divs:
            slug = "".join(d.xpath(".//a[@class='schoolNameLink']/@href"))
            page_url = f"https://www.tutortime.com{slug}"
            location_name = "".join(
                d.xpath(".//a[@class='schoolNameLink']//text()")
            ).strip()
            street_address = (
                d.xpath(".//span[@class='street']/text()")[0].strip() or "<MISSING>"
            )
            line = d.xpath(".//span[@class='cityState']/text()")[0].strip()
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            state = line.split()[0].strip()
            postal = line.split()[-1].strip()
            country_code = "US"
            store_number = get_id(slug)
            phone = (
                "".join(d.xpath(".//span[@class='tel']/text()")).strip() or "<MISSING>"
            )
            latitude = (
                d.xpath(".//span[@class='addr']/@data-latitude")[0] or "<MISSING>"
            )
            longitude = (
                d.xpath(".//span[@class='addr']/@data-longitude")[0] or "<MISSING>"
            )
            hours_of_operation = (
                "".join(d.xpath(".//p[@class='hours']/text()")).strip() or "<MISSING>"
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

    fox.close()

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
