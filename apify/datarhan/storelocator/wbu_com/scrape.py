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

    DOMAIN = "wbu.com"

    start_url = "https://8nzlzp5za2-2.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%20(lite)%203.30.0%3BJS%20Helper%202.26.1%3Bvue-instantsearch%201.7.0&x-algolia-application-id=8NZLZP5ZA2&x-algolia-api-key=f9564c6925184928d6f25d140fbc7942"
    body = '{"requests":[{"indexName":"wild_birds_site_locator","params":"query=&hitsPerPage=999&page=0&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&getRankingInfo=true&aroundLatLng=&aroundLatLngViaIP=false&aroundPrecision=1000&facets=%5B%5D&tagFilters="}]}'

    response = session.post(start_url, data=body)
    data = json.loads(response.text)
    for poi in data["results"][0]["hits"]:
        store_url = poi["ecommerceUrl"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["NAME"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["ADDR"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["CITY"]
        city = city if city else "<MISSING>"
        state = poi["STATE"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZIP"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["COUNTRY"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["KEY"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["PHONE"]
        phone = phone if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["LAT"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["LONG"]
        longitude = longitude if longitude else "<MISSING>"

        hours_of_operation = []
        hoo_url = "https://order.wbu.com/api/v1/customer/store/location/{}".format(
            poi["17"]
        )
        hoo_response = session.get(hoo_url)
        if "DOCTYPE html" not in hoo_response.text:
            hoo_data = json.loads(hoo_response.text)
            if hoo_data.get("storeTimings"):
                for elem in hoo_data["storeTimings"]:
                    hours_of_operation.append(
                        "{} {} - {}".format(
                            elem["day"], elem["openTime"], elem["closeTime"]
                        )
                    )
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
