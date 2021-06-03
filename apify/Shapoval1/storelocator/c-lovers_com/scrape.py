import csv
import json
import time
from sgselenium import SgSelenium
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

    locator_domain = "https://c-lovers.com"

    api_url = "https://c-lovers.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="more-link"]/a')
    for b in block:

        page_url = "".join(b.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        jsblock = (
            "["
            + "".join(tree.xpath('//script[contains(text(), "telephone")]/text()'))
            + "]"
        )
        hoosoo = "".join(tree.xpath('//span[@class="store-opening-soon"]/text()'))
        js = json.loads(jsblock)
        for j in js:
            location_name = j.get("name")

            location_type = j.get("@type")
            street_address = j.get("address").get("streetAddress")
            country_code = "CA"
            phone = j.get("telephone")
            state = j.get("address").get("addressRegion")

            city = j.get("address").get("addressLocality")
            store_number = "<MISSING>"
            try:
                hours_of_operation = (
                    " ".join(j.get("openingHours")).replace("[", "").replace("]", "")
                )
            except:
                hours_of_operation = "<MISSING>"
            if hoosoo:
                hours_of_operation = "Temporarily Closed"
            driver = SgSelenium().firefox()

            driver.get(page_url)
            iframe = driver.find_element_by_xpath("//div[@id='map']/iframe")
            driver.switch_to.frame(iframe)
            time.sleep(5)

            s = driver.find_element_by_xpath(
                "//div[@class='place-desc-large']/div[@class='address']"
            ).text

            time.sleep(5)
            driver.switch_to.default_content()
            postal = " ".join("".join(s).split(",")[-2].split()[1:])

            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
