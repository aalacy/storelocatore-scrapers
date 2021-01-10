import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests()

    items = []

    DOMAIN = "leosconeyisland.com"
    start_url = "https://www.leosconeyisland.com/Locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="dnnFormItem"]/div')
    for poi_html in all_locations:
        store_url = urljoin(start_url, poi_html.xpath(".//a/@href")[0])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath(".//a/strong/u/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//a[@style="text-decoration: underline;"]/text()'
        )
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//div[a[@style="text-decoration: underline;"]]/following-sibling::div[1]/text()'
        )[0].split(",")
        if len(raw_address) == 1:
            street_address += ", " + raw_address[0]
            raw_address = loc_dom.xpath(
                '//div[a[@style="text-decoration: underline;"]]/following-sibling::div[2]/text()'
            )[0].split(",")
        city = raw_address[0]
        state = raw_address[-1].split()[0]
        zip_code = raw_address[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = store_url.split("=")[-1]
        phone = loc_dom.xpath(
            '//div[a[@style="text-decoration: underline;"]]/following-sibling::div[2]/text()'
        )
        phone = phone[0].replace("(LEO1)", "") if phone else "<MISSING>"
        location_type = "<MISSING>"
        if "&spn" in loc_dom.xpath('//div[@class="google-maps"]/iframe/@src')[0]:
            geo = (
                loc_dom.xpath('//div[@class="google-maps"]/iframe/@src')[0]
                .split("&spn")[0]
                .split("=")[-1]
                .split(",")
            )
        else:
            geo = loc_dom.xpath('//div[@class="google-maps"]/iframe/@src')[0].split("=")
            geo = [elem for elem in geo if "%2C-" in elem]
            if geo:
                geo = geo[0].split("%2C")
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            latitude = geo[0]
            longitude = geo[1]
        hours_of_operation = loc_dom.xpath(
            '//div[a[@style="text-decoration: underline;"]]/following-sibling::div[4]/text()'
        )
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        if "Suit" in street_address:
            phone = loc_dom.xpath(
                '//div[a[@style="text-decoration: underline;"]]/following-sibling::div[3]/text()'
            )[0]
            hours_of_operation = loc_dom.xpath(
                '//div[a[@style="text-decoration: underline;"]]/following-sibling::div[5]/text()'
            )
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

        item = [
            DOMAIN,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
