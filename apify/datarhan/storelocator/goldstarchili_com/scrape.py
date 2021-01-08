import csv
import json
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

    DOMAIN = "goldstarchili.com"
    start_url = "https://www.goldstarchili.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    token = dom.xpath('//input[@name="__RequestVerificationToken"]/@value')[0]
    post_url = "https://www.goldstarchili.com/api/stores?handler=GetLocationsByZip"
    formdata = {
        "query": "10001",
        "__RequestVerificationToken": token,
        "X-Requested-With": "XMLHttpRequest",
    }
    response = session.post(post_url, data=formdata)
    data = json.loads(response.text)

    for poi in data:
        store_url = poi["momentFeedLocationUrl"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        location_type = "<MISSING>"
        city = poi["locality"]
        state = poi["region"]
        zip_code = poi["postcode"]
        country_code = poi["country"]
        store_number = poi["storeNumber"]
        phone = poi["phoneCleaned"]
        phone = phone if phone else "<MISSING>"
        latitude = poi["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"

        hdr = {"authorization": "IGBJZEVPPPHLPFCX"}
        loc_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?address={}&locality={}&multi_account=false&pageSize=30&region={}"
        loc_response = session.get(
            loc_url.format(
                street_address.replace(" ", "+"), city.replace(" ", "+"), state
            ),
            headers=hdr,
        )
        data = json.loads(loc_response.text)

        hours = data[0]["store_info"]["hours"].split(";")[:-1]
        hours = [elem[2:].replace(",", " - ").replace("00", ":00") for elem in hours]
        days = [
            "Monday",
            "Tuesday",
            "Wednsday",
            "Thursday",
            "Friday",
            "Satarday",
            "Sunday",
        ]
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
