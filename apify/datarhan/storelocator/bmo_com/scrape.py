import csv
import json
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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "bmo.com"
    start_url = "https://branchlocator.bmo.com/rest/locatorsearch?lang=en_US"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
    }
    all_codes = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=20,
        max_search_results=None,
    )
    for lat, lng in all_codes:
        body = '{"request":{"appkey":"343095D0-C235-11E6-93AB-1BF70C70A832","formdata":{"geoip":false,"dataview":"store_default","limit":50,"google_autocomplete":"true","geolocs":{"geoloc":[{"addressline":"","country":"","latitude":%s,"longitude":%s}]},"searchradius":"250","softmatch":"1","where":{"and":{"wheelchair":{"eq":""},"safedepositsmall":{"eq":""},"transit":{"eq":""},"languages":{"ilike":""},"saturdayopen":{"ne":""},"sundayopen":{"ne":""},"abmsaturdayopen":{"ne":""},"abmsundayopen":{"ne":""},"grouptype":{"eq":"BMOBranches"}}},"false":"0"}}}'
        response = session.post(start_url, data=body % (lat, lng), headers=headers)
        data = json.loads(response.text)

        if not data["response"].get("collection"):
            continue

        for poi in data["response"]["collection"]:
            store_url = "<MISSING>"
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["state"]
            if not state:
                state = poi["province"]
            state = state if state else "<MISSING>"
            zip_code = poi["postalcode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["uid"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["grouptype"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []
            hours = {}
            for key, value in poi.items():
                if key in ["grandopendate", "nowopen"]:
                    continue
                if not value:
                    continue
                if "abm" in key:
                    continue
                if "open" in key:
                    day = key.replace("open", "")
                    if "closed" in value:
                        hours[day] = "closed"
                    else:
                        closes = value[:-2] + ":" + value[-2:]
                        if hours.get(day):
                            hours[day]["open"] = closes
                        else:
                            hours[day] = {}
                            hours[day]["open"] = closes
                if "close" in key:
                    day = key.replace("close", "")
                    if "closed" in value:
                        hours[day] = "closed"
                    else:
                        closes = value[:-2] + ":" + value[-2:]
                        if hours.get(day):
                            hours[day]["close"] = closes
                        else:
                            hours[day] = {}
                            hours[day]["close"] = closes

            for day, time in hours.items():
                if time == "closed":
                    hours_of_operation.append("{} closed".format(day))
                else:
                    hours_of_operation.append(
                        "{} {} - {}".format(day, time["open"], time["close"])
                    )
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
            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
