from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import csv

from util import Util  # noqa: I900

myutil = Util()

session = SgRequests()

start_url = "https://www.cenex.com/locations"
locator_domain = "https://www.cenex.com/locations"
base_url = "https://www.cenex.com/Common/Services/InteractiveMap.svc/GetLocations"


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


def _payload(page, org_ids, loc_id, org_id, mapItemId):
    return {
        "AllOrganizationIds": org_ids.split("|"),
        "CurrentAmenities": [],
        "IsMobile": "true",
        "MapItemId": mapItemId,
        "MobileServiceUrl": "https://locatorservice.chsinc.ds/api/search/mobile",
        "SearchRequest": {
            "Metadata": {
                "Categories": [],
                "MapId": "",
                "PageNumber": page,
                "PageSize": "2000",
            },
            "Query": {
                "Amenities": [],
                "LocationTypes": loc_id.split("|"),
                "Organizations": [org_id],
                "SearchLat": "44.8697303",
                "SearchLong": "-93.0630684",
            },
        },
    }


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json; charset=utf-8",
        "Origin": "https://www.cenex.com",
        "Referer": "https://www.cenex.com/locations",
    }


def _type(type_id, types):
    res = "<MISSING>"
    for _ in types:
        if _["Id"] == type_id:
            res = _["Name"]
            break

    return res


def fetch_data():
    r = session.get(start_url)
    soup = bs(r.text, "lxml")
    org_id = soup.select_one("span#page_0_ddlLocationType")["organizationid"]
    loc_id = soup.select_one("span#page_0_ddlLocationType")["locationid"]
    org_ids = soup.select_one(
        "ul#exampleSelect1 li#page_0_rptLocationTypes_listLocationType_4"
    )["organizationid"]
    mapItemId = soup.select_one("#mapItemId")["value"]

    session.post(base_url, headers=_headers())
    data = []

    page = 1
    while True:
        res = session.post(
            base_url,
            json=_payload(page, org_ids, loc_id, org_id, mapItemId),
            headers=_headers(),
        )
        if not res.json()["SearchResponse"]:
            break

        locations = res.json()["SearchResponse"]["Locations"]
        if not locations:
            break

        location_types = res.json()["SearchResponse"]["Facets"]["LocationTypes"]
        for location in locations:
            page_url = locator_domain
            location_name = location["Name"]
            street_address = myutil._valid(
                location["Address1"] + " " + location["Address2"]
            )
            city = location["City"]
            state = location["State"]
            zip = location["Zip"]
            country_code = myutil.get_country_by_code(state)
            store_number = location["LocationId"]
            phone = location["Phone"]
            location_type = _type(location["TypeId"], location_types)
            latitude = location["Lat"]
            longitude = location["Long"]
            hours_of_operation = "<MISSING>"
            if location["Amenities"]:
                if location["Amenities"][0]["Name"].lower() == "24-hour fueling":
                    hours_of_operation = "24 hours"
            _item = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            myutil._check_duplicate_by_loc(data, _item)

        page += 1

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
