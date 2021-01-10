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

    DOMAIN = "txfb-ins.com"
    start_url = "https://web.txfb-ins.com/services/TFBIC.Services.RESTCounty.Lookup/REST_CountyLookup.svc/County"

    response = session.get(start_url)
    data = json.loads(response.text)
    all_counties = []
    for elem in data["_counties"]:
        all_counties.append(elem["_countyName"])

    for county in all_counties:
        store_url = "https://web.txfb-ins.com/services/TFBIC.Services.RESTCounty.Lookup/REST_CountyLookup.svc/County/{}".format(
            county
        )
        store_response = session.get(store_url)
        poi = json.loads(store_response.text)

        if not poi["_countyOffice"]:
            continue
        for office in poi["_countyOffice"]:
            store_url = "https://www.txfb-ins.com/county/details/{}".format(county)
            if office["_branchCode"]:
                store_url = "https://www.txfb-ins.com/county/details/{}/{}".format(
                    county, office["_branchCode"]
                )
            location_name = office["_agencyName"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = office["_physicalStreetAddress"]
            street_address = street_address if street_address else "<MISSING>"
            if office["_physicalStreetAddress2"]:
                street_address += ", " + office["_physicalStreetAddress2"]
            city = office["_physicalCity"]
            city = city if city else "<MISSING>"
            state = office["_physicalState"]
            state = state if state else "<MISSING>"
            zip_code = office["_mailingZip"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = office["_agencyCode"]
            store_number = store_number if store_number else "<MISSING>"
            phone = office["_phoneNumber"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = office["_latitude"]
            latitude = latitude[2:] if latitude else "<MISSING>"
            longitude = office["_longitude"]
            longitude = longitude.replace("-00", "-") if longitude else "<MISSING>"
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

            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
