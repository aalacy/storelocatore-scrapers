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

    DOMAIN = "underarmour.co.uk"
    start_url = (
        "https://hosted.where2getit.com/underarmour/2015/rest/locatorsearch?lang=en_US"
    )

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], max_radius_miles=50
    )
    body = '{"request":{"appkey":"24358678-428E-11E4-8BC2-2736C403F339","formdata":{"geoip":"start","dataview":"store_default","order":"UASPECIALITY, UAOUTLET, AUTHORIZEDDEALER, rank,_distance","limit":10,"geolocs":{"geoloc":[{"addressline":"","country":"","latitude":"%s","longitude":"%s"}]},"searchradius":"25|35|45|50|60|70|80|90|100|110|120|130|140|150|160|170|180|190|200|210|220|230|240|250","where":{"or":{"UASPECIALITY":{"eq":"1"},"UAOUTLET":{"eq":"1"},"AUTHORIZEDDEALER":{"eq":"1"}}}},"geoip":1}}'
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    for lat, lng in all_coords:
        response = session.post(start_url, data=body % (lat, lng), headers=headers)
        data = json.loads(response.text)
        if not data["response"].get("collection"):
            continue

        for poi in data["response"]["collection"]:
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address1"]
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
            if country_code != "UK":
                continue
            store_number = poi["clientkey"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            if poi["authorizeddealer"]:
                continue
            location_type = poi["dealertype"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []
            hours_dict = {}
            for key, value in poi.items():
                if "date" in key:
                    continue
                if "temp" in key:
                    continue
                if "close" in key:
                    day = key.replace("close", "")
                    if hours_dict.get(day):
                        hours_dict[day]["closes"] = value
                    else:
                        hours_dict[day] = {}
                        hours_dict[day]["closes"] = value
                if "open" in key:
                    day = key.replace("open", "")
                    if hours_dict.get(day):
                        hours_dict[day]["opens"] = value
                    else:
                        hours_dict[day] = {}
                        hours_dict[day]["closes"] = value
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            check = "{} {}".format(location_name, street_address)
            if check in scraped_items:
                continue
            store_url = "http://store-locations.underarmour.com/{}/{}/{}/".format(
                state, city.replace(" ", "-"), store_number
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

            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
