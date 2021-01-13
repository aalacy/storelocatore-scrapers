import csv
import json
from w3lib.url import add_or_replace_parameters

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

    DOMAIN = "chicosofftherack.com"
    start_url = "https://chicosofftherack.brickworksoftware.com/locations_search?hitsPerPage=15&page=0&getRankingInfo=true&facets[]=*&aroundRadius=all&filters=domain:chicosofftherack.brickworksoftware.com+AND+publishedAt%3C%3D1607683679661&esSearch=%7B%22page%22:0,%22storesPerPage%22:15,%22domain%22:%22chicosofftherack.brickworksoftware.com%22,%22locale%22:%22en_US%22,%22must%22:[%7B%22type%22:%22range%22,%22field%22:%22published_at%22,%22value%22:%7B%22lte%22:1607683679661%7D%7D],%22filters%22:[],%22aroundLatLngViaIP%22:true%7D&aroundLatLngViaIP=true"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    all_poi = []
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)
    all_poi += data["hits"]
    total_pages = data["nbPages"] + 2
    for page in range(0, total_pages):
        page_url = "https://chicosofftherack.brickworksoftware.com/locations_search?"
        params = {
            "hitsPerPage": "15",
            "page": str(page),
            "getRankingInfo": "true",
            "facets[]": "*",
            "aroundRadius": "all",
            "filters": "",
            "esSearch": '{"page":%s,"storesPerPage":15,"domain":"chicosofftherack.brickworksoftware.com","locale":"en_US","must":[{"type":"range","field":"published_at","value":{"lte":1607684950300}}],"filters":[],"aroundLatLng":{"lat":"40.581811","lon":"-74.166455"}}'
            % str(page),
            "aroundLatLng": "40.581811,-74.166455",
        }
        page_url = add_or_replace_parameters(start_url, params)
        response = session.get(page_url, headers=headers)
        data = json.loads(response.text)
        if not data.get("hits"):
            continue
        all_poi += data["hits"]

    for poi in all_poi:
        store_url = "https://stores.chicosofftherack.com/s/" + poi["attributes"]["slug"]
        location_name = poi["attributes"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["attributes"]["address1"]
        if poi["attributes"]["address2"]:
            street_address += " " + poi["attributes"]["address2"]
        if poi["attributes"]["address3"]:
            street_address += " " + poi["attributes"]["address1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["attributes"]["city"]
        city = city if city else "<MISSING>"
        state = poi["attributes"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["attributes"]["postalCode"]
        country_code = poi["attributes"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["attributes"]["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["attributes"]["type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["attributes"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["attributes"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["relationships"]["hours"]:
            if elem["type"] != "regular":
                continue
            day = elem["displayDay"]
            opens = elem["displayStartTime"]
            closes = elem["displayEndTime"]
            hours_of_operation.append(f"{day} {opens} - {closes}")
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
        check = "{} {}".format(location_name, street_address)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
