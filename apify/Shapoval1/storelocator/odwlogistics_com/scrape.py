import csv
import time
import usaddress
from lxml import html
from sgrequests import SgRequests
from sgselenium import SgSelenium


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

    locator_domain = "https://www.odwlogistics.com"
    api_url = "https://www.odwlogistics.com/locations-and-reach"
    session = SgRequests()
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[contains(@class, "location--teaser__facility location--teaser")]'
    )
    for d in div:
        slug = "".join(d.xpath(".//a[@class='location--teaser__url link']/@href"))
        location_name = "".join(
            d.xpath('.//div[@class="location--teaser__name"]//text()')
        )
        street_address = (
            "".join(d.xpath('.//ul[@class="location--teaser__specs"]/li[4]/text()'))
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = "".join(
                d.xpath('.//ul[@class="location--teaser__specs"]/li[3]/text()')
            )
        phone = (
            "".join(d.xpath('.//ul[@class="location--teaser__specs"]/li[5]/a/text()'))
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = "".join(
                d.xpath('.//ul[@class="location--teaser__specs"]/li[4]/a/text()')
            )
        page_url = f"{locator_domain}{slug}"
        driver = SgSelenium().firefox()

        driver.get(page_url)

        iframe = driver.find_element_by_xpath('//iframe[contains(@src, "maps")]')
        driver.switch_to.frame(iframe)
        time.sleep(10)
        ad = driver.find_element_by_xpath("//div[@class='address']").text
        location_type = "<MISSING>"
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "USA"
        city = a.get("city") or "<MISSING>"
        store_number = "<MISSING>"
        latlon = driver.find_element_by_xpath(
            '//a[text()="View larger map"]'
        ).get_attribute("href")
        try:
            latitude = "".join(latlon).split("ll=")[1].split(",")[0].strip()
            longitude = (
                "".join(latlon).split("ll=")[1].split(",")[1].split("&")[0].strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = "<MISSING>"
        driver.switch_to.default_content()

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
