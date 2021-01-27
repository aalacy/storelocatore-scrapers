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

    DOMAIN = "callitspring.com"
    start_url = "https://www.callitspring.com/api/stores?allStores=true&countryCode=CA&lat=45.62838199999999&lng=-73.5512572"
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-aldo-api-version": "2",
        "x-aldo-brand": "callitspring",
        "x-aldo-lang": "en",
        "x-aldo-region": "ca",
        "x-aldo-ssr-request-id": "",
        "x-forwarded-akamai-edgescape": "undefined",
    }
    all_locations = []
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)
    all_locations += data["stores"]

    start_url = "https://www.callitspring.com/api/stores?allStores=true&countryCode=US&lat=45.62838199999999&lng=-73.5512572"
    headers["x-aldo-region"] = "us"
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)
    all_locations += data["stores"]

    for poi in all_locations:
        poi_name = poi["name"]
        poi_url = "https://www.callitspring.com/ca/en/store-locator/store/{}".format(
            poi_name
        )
        poi_name = poi_name if poi_name else "<MISSING>"
        street = poi["address"]["line1"]
        street = street if street else "<MISSING>"
        city = poi["address"]["town"]
        city = city if city else "<MISSING>"
        state = poi["address"]["region"]["isocodeShort"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["region"]["countryIso"]
        country_code = country_code if country_code else "<MISSING>"
        poi_number = poi_name
        poi_number = poi_number if poi_number else "<MISSING>"
        phone = poi["address"]["phone"]
        phone = phone if phone else "<MISSING>"
        poi_type = poi["storeType"]
        poi_type = poi_type if poi_type else "<MISSING>"
        latitude = poi["geoPoint"]["latitude"]
        longitude = poi["geoPoint"]["longitude"]
        hoo = []
        for elem in poi["openingHours"]["weekDayOpeningList"]:
            if elem.get("openingTime"):
                day = elem["weekDay"]
                opens = elem["openingTime"]["formattedHour"]
                closes = elem["closingTime"]["formattedHour"]
                hoo.append(f"{day} {opens} - {closes}")
            else:
                hoo.append(f"{day} closed")
        hoo = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            DOMAIN,
            poi_url,
            poi_name,
            street,
            city,
            state,
            zip_code,
            country_code,
            poi_number,
            phone,
            poi_type,
            latitude,
            longitude,
            hoo,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
