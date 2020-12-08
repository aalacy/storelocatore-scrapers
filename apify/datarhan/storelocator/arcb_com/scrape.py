import csv
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

from sgrequests import SgRequests

DOMAIN = "americasbest.com"


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "arcb.com"
    start_url = "https://arcb.com/tools/service-search.html"
    session.get(start_url)

    suggest_forzip_body = '{"accountForConsigneeRoutingExceptions":false,"paymentTerms":"NotSpecified","isConsigneeCodingRequired":false,"isThirdPartyCodingRequired":false,"isFourthPartyCodingRequired":false,"isRemitToPartyCodingRequired":false,"isOtherPartyCodingRequired":false,"shipper":{"locationToCode":{"city":"","state":"","zip":"%s","country":"%s","allowPoBoxes":false,"allowNotServedLocations":false}}}'
    suggest_url = "https://arcb.com/ajax/apipassthrough/passthrough.html"
    sug_headers = {
        "authority": "arcb.com",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "x-abf-api-destination": "https://apps.abf.com/api/coding/",
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        max_radius_miles=20,
        max_search_results=None,
    )

    for code in all_codes:
        if len(code.split()[0]) > 3:
            body = suggest_forzip_body % (code.replace(" ", "+"), "US")
        else:
            body = suggest_forzip_body % (code + "0A1", "CA")
        sug_response = session.post(suggest_url, data=body, headers=sug_headers)
        sug_data = sug_response.json()
        if "Invalid ZIP Code" in sug_response.text:
            continue
        if "This location is not served" in sug_response.text:
            continue
        if "We do not pickup from or deliver to PO Boxes" in sug_response.text:
            continue
        if sug_data["errors"]:
            if not sug_data["errors"][0].get("similarZips"):
                continue
        if not sug_data["codedShipperLocation"]:
            multi_result = sug_data["errors"][0]["similarZips"][0]
            city = multi_result["city"]
            country = multi_result["country"]
            state = multi_result["state"]
            zip_code = multi_result["zipRangeHigh"]
        else:
            city = sug_data["codedShipperLocation"]["city"]
            country = sug_data["codedShipperLocation"]["country"]
            state = sug_data["codedShipperLocation"]["state"]
            zip_code = sug_data["codedShipperLocation"]["zip"]

        results_url = "https://arcb.com/ajax/apipassthrough/passthrough.html?city={}&country={}&state={}&zip={}"
        results_url = results_url.format(
            city.replace(" ", "+"), country, state, zip_code.replace(" ", "+")
        )
        api_path = "https://apps.abf.com/api/abf-network/routing?city={}&country={}&state={}&zip={}"
        api_path = api_path.format(
            city.replace(" ", "+"), country, state, zip_code.replace(" ", "+")
        )
        results_headers = {
            "authority": "arcb.com",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
            "x-abf-api-destination": api_path,
        }
        results_response = session.get(results_url, headers=results_headers)
        results_headers = {
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
            "x-abf-api-destination": "https://apps.abf.com/api/abf-network/routing?city=BEVERLY+HILLS&country=US&state=CA&zip=90210",
        }
        results_data = results_response.json()
        if not results_data.get("locations"):
            continue

        for poi in results_data["locations"]:
            detail_url = "https://arcb.com/ajax/apipassthrough/passthrough.html"
            api_path_detail = (
                "https://apps.abf.com/api/abf-network/stations/{}/detailed".format(
                    poi["station"]["stationNumber"]
                )
            )
            detail_headers = {
                "accept": "application/json, text/plain, */*",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
                "x-abf-api-destination": api_path_detail,
            }
            detail_response = session.get(detail_url, headers=detail_headers)
            detail_data = detail_response.json()

            store_url = "<MISSING>"
            location_name = "{}, {} Service Center".format(
                detail_data["station"]["title"],
                detail_data["station"]["location"]["state"],
            )
            location_name = location_name if location_name else "<MISSING>"
            street_address = detail_data["station"]["location"]["address"]
            street_address = street_address if street_address else "<MISSING>"
            city = detail_data["station"]["location"]["city"]
            city = city if city else "<MISSING>"
            state = detail_data["station"]["location"]["state"]
            state = state if state else "<MISSING>"
            zip_code = detail_data["station"]["location"]["zip"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = detail_data["station"]["location"]["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = detail_data["station"]["stationNumber"]
            phone = detail_data["station"]["interstatePhone"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"

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
