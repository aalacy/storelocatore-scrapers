import csv
from lxml import etree

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

    DOMAIN = "rocketfizz.com"
    start_url = "https://rocketfizz.com/?sl_engine=sl-xml"

    response = session.get(start_url)
    dom = etree.XML(response.text)
    all_locations = dom.xpath("//marker")

    for poi_html in all_locations:
        store_url = poi_html.xpath("@url")[0]
        location_name = poi_html.xpath("@name")[0].replace("&#44;", ",")
        street_address = poi_html.xpath("@street")[0].replace("&#44;", ",")
        city = poi_html.xpath("@city")[0]
        state = poi_html.xpath("@state")[0]
        zip_code = poi_html.xpath("@zip")[0]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath("@phone")[0].replace("(FIZZ)", "")
        phone = phone.replace("?", "") if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath("@lat")[0]
        longitude = poi_html.xpath("@lng")[0]

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        days = loc_dom.xpath("//table/tbody/tr/td[1]/text()")[1:]
        if not days:
            days = loc_dom.xpath('//td[contains(text(), "Hours:")]/text()')[1:]
        days = [elem.strip() for elem in days]
        hours = loc_dom.xpath("//table/tbody/tr/td[2]/text()")[1:]
        if not hours:
            hours = loc_dom.xpath(
                '//td[contains(text(), "Hours:")]/following-sibling::td/text()'
            )[1:]
        hours = [elem.strip() for elem in hours]
        hours_of_operation = list(map(lambda day, hour: day + " " + hour, days, hours))
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
