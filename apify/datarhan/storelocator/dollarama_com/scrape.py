import csv
import json
from time import sleep
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "dollarama.com"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    start_url = "https://www.dollarama.com/en-CA/locations/GetDataByCoordinates?longitude={}&latitude={}&distance=500&units=kilometers&amenities=&paymentMethods="
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        max_radius_miles=100,
        max_search_results=None,
    )

    for lat, lng in all_coordinates:
        response = session.post(start_url.format(lng, lat), headers=hdr)
        passed = False
        if "This request has been rate-limited." in response.text:
            while not passed:
                sleep(300)
                response = session.post(start_url.format(lng, lat), headers=hdr)
                if "This request has been rate-limited." not in response.text:
                    passed = True

        all_poi_data = json.loads(response.text)
        for poi in all_poi_data["StoreLocations"]:
            location_name = poi["Name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["ExtraData"]["Address"]["AddressNonStruct_Line1"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["ExtraData"]["Address"]["Locality"]
            city = city if city else "<MISSING>"
            state = poi["ExtraData"]["Address"]["Region"]
            state = state if state else "<MISSING>"
            zip_code = poi["ExtraData"]["Address"]["PostalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["ExtraData"]["Address"]["CountryCode"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["LocationNumber"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["ExtraData"]["Phone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["Location"]["type"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["Location"]["coordinates"][-1]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["Location"]["coordinates"][0]
            longitude = longitude if longitude else "<MISSING>"
            store_url = "https://www.dollarama.com/en-CA/locations/{}/{}-{}".format(
                state.replace(" ", "-").replace(".", ""),
                city.replace(" ", "-").replace(".", ""),
                street_address.split(",")[0].replace(" ", "-").replace(".", ""),
            )

            hours_of_operation = []
            days = {
                "Mo": "Monday",
                "Tu": "Tuesday",
                "We": "Wednesday",
                "Th": "Thursday",
                "Fr": "Friday",
                "Sa": "Saturday",
                "Su": "Sunday",
            }

            hours = poi["ExtraData"]["HoursOfOpStruct"]
            hours_of_operation = []
            if hours:
                for key, day_name in days.items():
                    if hours[key]["Ranges"]:
                        start = hours[key]["Ranges"][0]["StartTime"]
                        end = hours[key]["Ranges"][0]["EndTime"]
                        hours_of_operation.append(
                            "{} {} - {}".format(day_name, start, end)
                        )
                    else:
                        hours_of_operation.append("{} closed".format(day_name))

            hours_of_operation = ", ".join(hours_of_operation)

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
