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

    DOMAIN = "bankatpeoples.com"
    start_url = "https://bankatpeoplesv1.locatorsearch.com/GetItems.aspx"

    formdata = {
        "lat": "42.205798",
        "lng": "-72.60851",
        "searchby": "FCS|",
        "SearchKey": "",
        "rnd": "1612433817151",
    }
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    }
    response = session.post(start_url, data=formdata, headers=headers)
    dom = etree.XML(
        response.text.replace(
            '<?xml version="1.0" encoding="utf-8" standalone="yes" ?>', ""
        )
    )

    all_locations = dom.xpath("//marker")
    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath(".//title/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath(".//add1/text()")
        street_address = street_address[0] if street_address else "<MISSING>"
        raw_data = poi_html.xpath(".//add2/text()")[0].split("<")[0].split(", ")
        city = raw_data[0]
        state = raw_data[-1].split()[0]
        zip_code = raw_data[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath(".//add2/text()")[0].split("<b>")[-1].split("<")[0]
        location_type = "<MISSING>"
        latitude = poi_html.xpath("@lat")[0]
        longitude = poi_html.xpath("@lng")[0]
        hoo = etree.HTML(poi_html.xpath(".//contents/text()")[0])
        hoo = [elem.strip() for elem in hoo.xpath("//text()")[1:] if elem.strip()]
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
