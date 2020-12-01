import csv
import json
import sgzip
from sgrequests import SgRequests
from sgzip import SearchableCountries


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

    DOMAIN = "bbvausa.com"

    all_codes = []
    us_zips = sgzip.for_radius(radius=100, country_code=SearchableCountries.USA)
    for zip_code in us_zips:
        all_codes.append(zip_code)

    for code in all_codes:
        start_url = (
            "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?v=20190101&api_key=7d3f010c5d39e1427b1ef79803fb493e&jsLibVersion=v0.9.2&input="
            + code
            + "%20me&experienceKey=bbvaconfig&version=PRODUCTION&filters=%7B%22%24or%22%3A%5B%7B%22c_bBVAType%22%3A%7B%22%24eq%22%3A%22BBVA%20Branch%22%7D%7D%2C%7B%22c_bBVAType%22%3A%7B%22%24eq%22%3A%22BBVA%20ATM%22%7D%7D%5D%7D&verticalKey=locations&locale=en"
        )
        response = session.get(start_url)

        data = json.loads(response.text)
        for poi in data["response"]["results"]:
            location_name = poi["data"].get("c_bBVAName")
            if not location_name:
                location_name = poi["data"]["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["data"]["address"]["line1"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["data"]["address"]["city"]
            city = city if city else "<MISSING>"
            state = poi["data"]["address"]["region"]
            state = state if state else "<MISSING>"
            zip_code = poi["data"]["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["data"]["address"]["countryCode"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["data"]["id"]
            phone = poi["data"]["mainPhone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["data"]["c_bBVAType"][0]
            location_type = location_type if location_type else "<MISSING>"
            if poi["data"].get("cityCoordinate"):
                latitude = poi["data"]["cityCoordinate"]["latitude"]
                longitude = poi["data"]["cityCoordinate"]["longitude"]
            else:
                latitude = poi["data"]["displayCoordinate"]["latitude"]
                longitude = poi["data"]["displayCoordinate"]["longitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []
            if poi["data"].get("hours"):
                for day, hours in poi["data"]["hours"].items():
                    if type(hours) == str:
                        continue
                    if day == "holidayHours":
                        continue
                    if hours.get("openIntervals"):
                        hours_of_operation.append(
                            "{} {} - {}".format(
                                day,
                                hours["openIntervals"][0]["start"],
                                hours["openIntervals"][0]["end"],
                            )
                        )
                    if hours.get("isClosed"):
                        hours_of_operation.append("{} - closed".format(day))
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            store_url = poi["data"].get("url")
            if not store_url:
                store_url = "https://www.bbvausa.com/USA/{}/{}/{}/".format(
                    state, city, street_address
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

            if location_name not in scraped_items:
                scraped_items.append(location_name)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
