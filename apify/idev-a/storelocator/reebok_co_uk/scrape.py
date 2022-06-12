import csv
from sgrequests import SgRequests
import json

from util import Util  # noqa: I900

myutil = Util()


session = SgRequests()


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
    data = []

    locator_domain = "https://www.reebok.co.uk/"
    base_url = "https://placesws.adidas-group.com/API/search?brand=reebok&geoengine=google&method=get&category=store&latlng=54.364643026217735%2C-7.3957917936926165%2C15551&page=1&pagesize=500&fields=name%2Cstreet1%2Cstreet2%2Caddressline%2Cbuildingname%2Cpostal_code%2Ccity%2Cstate%2Cstore_o+wner%2Ccountry%2Cstoretype%2Clongitude_google%2Clatitude_google%2Cstore_owner%2Cstate%2Cperformance%2Cbrand_store%2Cfactory_outlet%2Coriginals%2Cneo_label%2Cy3%2Cslvr%2Cchildren%2Cwoman%2Cfootwear%2Cfootball%2Cbasketball%2Coutdoor%2Cporsche_design%2Cmiadidas%2Cmiteam%2Cstella_mccartney%2Ceyewear%2Cmicoach%2Copening_ceremony%2Coperational_status%2Cfrom_date%2Cto_date%2Cdont_show_country&format=json&storetype="
    detail_url = "https://placesws.adidas-group.com/API/detail?brand=reebok&method=get&category=store&objectId={}&format=json"
    rr = session.get(base_url)
    locations = json.loads(rr.text)["wsResponse"]["result"]
    for location in locations:
        location_name = location["name"]
        if "reebok" not in location_name.lower() or location["country"] != "GB":
            continue
        store_number = location["id"]
        country_code = location["country"]
        page_url = "<MISSING>"
        city = location["city"]
        state = "<MISSING>"
        zip = location["postal_code"]
        street_address = location["street1"]
        location_type = myutil._valid(location.get("storetype"))
        latitude = location["latitude_google"]
        longitude = location["longitude_google"]
        r1 = session.get(detail_url.format(store_number))
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        detail = json.loads(r1.text)["wsResponse"]["result"]
        if detail:
            detail = detail[0]
            phone = detail.get("phone", "<MISSING>").strip()
            try:
                hours = []
                hours.append(f"Mon: {detail['openinghours_Monday']}")
                hours.append(f"Tue: {detail['openinghours_Tuesday']}")
                hours.append(f"Wed: {detail['openinghours_Wednesday']}")
                hours.append(f"Thu: {detail['openinghours_Thursday']}")
                hours.append(f"Fri: {detail['openinghours_Friday']}")
                hours.append(f"Sat: {detail['openinghours_Saturday']}")
                hours.append(f"Sun: {detail['openinghours_Sunday']}")
                hours_of_operation = "; ".join(hours)
            except:
                pass

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

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
