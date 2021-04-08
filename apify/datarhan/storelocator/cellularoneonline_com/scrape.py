import csv
from lxml import etree

from sgrequests import SgRequests
from sgselenium import SgFirefox


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

    DOMAIN = "cellularoneonline.com"
    start_url = "https://mycellularone.com/locations/"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
    all_locations = dom.xpath('//article[contains(@class, "locations")]')

    post_url = "https://mycellularone.com/wp-admin/admin-ajax.php"
    for poi_html in all_locations:
        store_number = poi_html.xpath("@data-post-id")[0]
        frm = {
            "action": "locations_location_detail",
            "location_id": str(store_number),
            "neighbors[]": "997",
            "neighbors[]": "424",
            "neighbors[]": "1090",
            "neighbors[]": "1091",
            "neighbors[]": "1092",
            "neighbors[]": "462",
            "neighbors[]": "1094",
            "neighbors[]": "1095",
            "neighbors[]": "1096",
            "neighbors[]": "464",
            "neighbors[]": "463",
            "neighbors[]": "1097",
            "neighbors[]": "1098",
            "neighbors[]": "1099",
        }

        hdr = {
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://mycellularone.com",
            "referer": "https://mycellularone.com/locations/",
            "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        loc_response = session.post(post_url, data=frm, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        store_url = start_url
        location_name = poi_html.xpath('.//div[@class="location-name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = poi_html.xpath(".//address/text()")[0].split(":")[-1].split("\n")
        street_address = raw_data[0].strip()
        city = raw_data[-1].split(", ")[0]
        state = raw_data[-1].split(", ")[-1].split()[0]
        zip_code = raw_data[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath("@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath("@data-lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="nmld-detail-item for-hours"]/text()')
        hoo = [elem.strip() for elem in hoo]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
