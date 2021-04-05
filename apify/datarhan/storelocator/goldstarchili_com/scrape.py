import csv
import json

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
    scraped_items = []

    DOMAIN = "goldstarchili.com"
    start_url = "https://api.momentfeed.com/v1/analytics/api/v2/llp/sitemap?auth_token=IGBJZEVPPPHLPFCX&country=US&multi_account=false"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["locations"]:
        address = poi["store_info"]["address"].replace(" ", "+")
        locality = poi["store_info"]["locality"].replace(" ", "+")
        region = poi["store_info"]["region"]
        url = "https://api.momentfeed.com/v1/analytics/api/llp.json?address={}&locality={}&multi_account=false&pageSize=30&region={}"
        url = url.format(address, locality, region)
        hdr = {"authorization": "IGBJZEVPPPHLPFCX"}
        loc_response = session.get(url, headers=hdr)
        data = json.loads(loc_response.text)

        store_url = "https://locations.goldstarchili.com" + data[0]["llp_url"]
        location_name = [
            elem["data"]
            for elem in data[0]["custom_fields"]
            if elem["name"] == "LLP_Name"
        ]
        location_name = (
            location_name[0] if location_name else data[0]["store_info"]["name"]
        )
        location_name = location_name if location_name else "<MISSING>"
        street_address = data[0]["store_info"]["address"]
        location_type = "<MISSING>"
        city = data[0]["store_info"]["locality"]
        state = data[0]["store_info"]["region"]
        zip_code = data[0]["store_info"]["postcode"]
        country_code = data[0]["store_info"]["country"]
        store_number = data[0]["store_info"]["corporate_id"]
        phone = data[0]["store_info"]["phone"]
        phone = phone if phone else "<MISSING>"
        latitude = data[0]["store_info"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = data[0]["store_info"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = ""
        if type(data) == list:
            hours = data[0]["store_info"]["hours"].split(";")[:-1]
            hours = [elem[2:].replace(",", " - ") for elem in hours]

            days = [
                "Monday",
                "Tuesday",
                "Wednsday",
                "Thursday",
                "Friday",
                "Satarday",
                "Sunday",
            ]
            hours_of_operation = list(
                map(lambda day, hour: day + " " + hour, days, hours)
            )
        hours_of_operation = (
            " ".join(hours_of_operation)
            .replace("00 -", ":00 -")
            .replace("00", ":00")
            .replace("::", ":")
            .replace("30", ":30")
            if hours_of_operation
            else "<MISSING>"
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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
