import csv
import json
from lxml import etree

from sgzip.dynamic import DynamicZipSearch, SearchableCountries
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

    DOMAIN = "dollartree.com"

    response = session.get("https://www.dollartree.com/locations/")
    dom = etree.HTML(response.text)
    url_dict = {}
    all_states = dom.xpath("//a[@data-galoc]/@href")[2:]
    for url in all_states:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_cities = dom.xpath('//td[h2[@class="citiesclass"]]//a/@href')
        for url in all_cities:
            response = session.get(url)
            dom = etree.HTML(response.text)
            all_locations = dom.xpath('//div[@class="storeinfo_div "]')
            for loc in all_locations:
                loc_url = loc.xpath(".//a/@href")[0]
                street_address = (
                    loc.xpath(".//@data-galoc")[0].split(",")[0].split("- ")[-1]
                )
                url_dict[street_address] = loc_url

    start_url = (
        "https://hosted.where2getit.com/dollartree/rest/locatorsearch?lang=en_US"
    )
    hdr = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        max_search_distance_miles=200,
        max_search_results=None,
    )
    for code in all_codes:
        body = '{"request":{"appkey":"134E9A7A-AB8F-11E3-80DE-744E58203F82","formdata":{"geoip":false,"dataview":"store_default","limit":1000,"order":"_DISTANCE","geolocs":{"geoloc":[{"addressline":"%s","country":"","latitude":"","longitude":""}]},"searchradius":"500","radiusuom":"","where":{"icon":{"eq":""},"ebt":{"eq":""},"freezers":{"eq":""},"crafters_square":{"eq":""},"snack_zone":{"eq":""},"distributioncenter":{"distinctfrom":"1"}},"false":"0"}}}'
        response = session.post(start_url, data=body % code, headers=hdr)

        data = json.loads(response.text)

        if not data["response"].get("collection"):
            continue

        for poi in data["response"]["collection"]:
            store_url = "<MISSING>"
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address1"]
            if poi.get("address2"):
                street_address += " " + poi["address2"]
            if poi.get("address3"):
                street_address += " " + poi["address3"]
            street_address = street_address if street_address else "<MISSING>"
            for k, v in url_dict.items():
                if k in street_address:
                    store_url = v
                    break
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
            store_number = poi["clientkey"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = poi["hours"]
            if poi["hours2"]:
                hours_of_operation += ", " + poi["hours2"]
            if not hours_of_operation:
                hours_of_operation = []
                for key, value in poi.items():
                    if "hours" in key:
                        if not value:
                            continue
                        hours_of_operation.append(value)
                hours_of_operation = ", ".join(hours_of_operation)
            hours_of_operation = (
                hours_of_operation if hours_of_operation else "<MISSING>"
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
