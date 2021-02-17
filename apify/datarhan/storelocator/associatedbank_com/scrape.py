import re
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

    DOMAIN = "associatedbank.com"
    start_url = "https://spatial.virtualearth.net/REST/v1/data/e0ac722002794ad6b6cb3e5b3320e23b/AssociatedProduction/AssociatedBank?$filter=Branch%20Eq%27Yes%27%20Or%20ATM%20Eq%27Yes%27%20Or%20NonBranchLocation%20Eq%27Yes%27&spatialFilter=nearby({},{},%2080%20)&$select=EntityID,AddressLine,Latitude,Longitude,PostalCode,DriveUpHours,LobbyHours,LocationName,PrimaryCity,State,Phone,ATM,Branch,DAATMs,MortgageOfficer,AISRep,SafeDepositBox,PrivateClient,InstitutionalTrust,InstantIssueCards,NonBranchLocation&$*&$format=json&jsonp=SDSServiceCallback&key=Apc8XDQjnMpfQnJXz8qbV_y8lRaMTqq35W_gbey3U-P3j2EmFs7eCjLO-fofpeMJ"
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=30,
        max_search_results=None,
    )
    for lat, lng in search:
        response = session.get(start_url.format(lat, lng))
        data = re.findall(r"ServiceCallback\((.+)\)", response.text)[0]
        data = json.loads(data)

        for poi in data["d"]["results"]:
            store_url = "<MISSING>"
            location_name = poi["LocationName"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["AddressLine"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["PrimaryCity"]
            city = city if city else "<MISSING>"
            state = poi["State"]
            state = state if state else "<MISSING>"
            zip_code = poi["PostalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "USA"
            store_number = poi["EntityID"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["Phone"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            if poi["Branch"] == "Yes":
                location_type = "Branch"
            else:
                location_type = "ATM"
            latitude = poi["Latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["Longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = poi["LobbyHours"].replace("/", "")
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
            check = "{} {}".format(street_address, location_name)
            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
