import csv
import json

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


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

    DOMAIN = "eatnpark.com"
    start_url = "https://hosted.where2getit.com/eatnpark/rest/locatorsearch?lang=en_US"

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )
    for lat, lng in all_coordinates:
        body = '{"request":{"appkey":"90D3A4D8-B844-3CAC-BD6F-79DDE6FAF9BC","formdata":{"geoip":true,"dataview":"store_default","geolocs":{"geoloc":[{"addressline":"","country":"","latitude":"%s","longitude":"%s"}]},"searchradius":"200","where":{"PICKUP_WINDOW":{"eq":""},"MEETING_ROOM":{"eq":""},"FLAG24HOUR":{"eq":""},"outdoor_dining":{"eq":""},"curbside":{"eq":""},"delivery":{"eq":""}},"true":"1"},"geoip":1}}'
        hdr = {"X-Requested-With": "XMLHttpRequest"}
        response = session.post(start_url, data=body % (lat, lng), headers=hdr)
        data = json.loads(response.text)
        if not data["response"].get("collection"):
            continue
        all_locations += data["response"]["collection"]

    for poi in all_locations:
        store_url = poi["online_ordering"]
        street_address = poi["address1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        store_number = poi["clientkey"]
        location_name = poi["name"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hours_of_operation = []
        days_keys = [
            "sunday",
            "thursday",
            "wednesday",
            "tuesday",
            "friday",
            "monday",
            "saturday",
        ]
        for elem in days_keys:
            hours_of_operation.append("{} - {}".format(elem, poi[elem]))
        hours_of_operation = (
            " ".join(hours_of_operation).replace("TAKEOUT ONLY", "")
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
