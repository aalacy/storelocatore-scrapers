import csv
import json
import sgzip
from sgzip import SearchableCountries

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
    scrape_items = []

    DOMAIN = "dhl.com"
    start_url = "https://wsbexpress.dhl.com/ServicePointLocator/restV3/servicepoints?servicePointResults=50&address={}&countryCode=US&capability=80,86,87&weightUom=lb&dimensionsUom=in&languageScriptCode=Latn&language=eng&languageCountryCode=GB&resultUom=mi&b64=true&key=963d867f-48b8-4f36-823d-88f311d9f6ef"

    all_codes = []
    us_zips = sgzip.for_radius(radius=50, country_code=SearchableCountries.USA)
    for zip_code in us_zips:
        all_codes.append(zip_code)
    ca_zips = sgzip.for_radius(radius=50, country_code=SearchableCountries.USA)
    for zip_code in ca_zips:
        all_codes.append(zip_code)

    for code in all_codes:
        response = session.get(start_url.format(code))
        if not response.text:
            continue

        data = json.loads(response.text)

        if not data.get("servicePoints"):
            continue

        for poi in data["servicePoints"]:
            store_url = poi.get("contactDetails", {}).get("linkUri")
            store_url = store_url if store_url else "<MISSING>"
            location_name = poi["servicePointName"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]["addressLine1"]
            if poi["address"]["addressLine2"]:
                street_address += ", " + poi["address"]["addressLine2"]
            if poi["address"]["addressLine3"]:
                street_address += ", " + poi["address"]["addressLine3"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["address"]["city"]
            city = city if city else "<MISSING>"
            state = poi["address"]["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["address"]["zipCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["address"]["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["facilityId"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["contactDetails"].get("phoneNumber")
            phone = phone if phone else "<MISSING>"
            location_type = poi["servicePointType"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["geoLocation"]["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["geoLocation"]["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []
            for elem in poi["openingHours"]["openingHours"]:
                day = elem["dayOfWeek"]
                opens = elem["openingTime"]
                closes = elem["closingTime"]
                hours_of_operation.append("{} {} - {}".format(day, opens, closes))
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
            if store_number not in scrape_items:
                scrape_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
