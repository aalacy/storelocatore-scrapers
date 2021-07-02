import csv
import usaddress
from sgrequests import SgRequests
from bs4 import BeautifulSoup


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    base_url = "https://www.fasttrackurgentcare.com/locations-and-hours/"
    r = session.get(base_url)
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    soup = BeautifulSoup(r.text, "html.parser")
    return_main_object = []
    main = soup.find("div", {"id": "accordionExample"}).find_all(
        "div", {"class": "card"}
    )
    for location in main:
        lat = location.find("button")["data-lat"]
        lng = location.find("button")["data-lng"]
        name = location.find("button")["data-title"]

        st = (
            location.find("button")["data-address"]
            + " "
            + location.find("button")["data-citystzip"]
        )
        a = usaddress.tag(st, tag_mapping=tag)[0]
        address = f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
        zip = a.get("postal")
        state = a.get("state")
        city = a.get("city")
        dt = list(
            location.find("div", {"class": "card-content text-left"}).stripped_strings
        )
        hours = dt[4] + " " + dt[5]
        phone = dt[3]
        if "Learn" in hours:
            hours = dt[3] + " " + dt[4]
            phone = dt[2]
        page_url = location.find("a", {"class": "btn-sm btn-secondary-sm"})["href"]

        store = []
        store.append("hhttps://www.fasttrackurgentcare.com")
        store.append(page_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("fasttrackurgentcare")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
