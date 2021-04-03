import csv
import usaddress
from sgrequests import SgRequests
from bs4 import BeautifulSoup


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    data = "countryCode=US"
    r = session.post(
        "https://www.ethanallen.com/on/demandware.store/Sites-ethanallen-us-Site/en_US/Stores-GetStatesByCountry",
        headers=headers,
        data=data,
    )
    return_main_object = []
    state_data = r.json()["states"]
    for state in state_data:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
        }
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
        state_request = session.get(
            "https://www.ethanallen.com/on/demandware.store/Sites-ethanallen-us-Site/en_US/Stores-GetStoreListByCountryAndState?countryCode=US&stateCode="
            + state["code"],
            headers=headers,
        )
        state_soup = BeautifulSoup(state_request.text, "lxml")
        for location in state_soup.find_all("div", {"class": "store"}):
            name = location.find("h3").text
            address = list(location.find("p", {"class": "address"}).stripped_strings)
            address = " ".join(address)
            a = usaddress.tag(address, tag_mapping=tag)[0]
            store_id = location["data-id"]
            phone = location["data-phone"]
            hours = (
                " ".join(list(location.find_all("li")[1].stripped_strings))
                .replace("\n", "")
                .strip()
            )

            hours = (
                hours.replace("Appointments Encouraged", "")
                .replace("By Appointment", "")
                .replace("and by appointment", "")
                .replace("Evenings by Appointment", "")
                .replace("By Appointment Only", "")
                .strip()
            )
            if hours.find("temporary closed ") != -1:
                hours = "temporary closed"
            if hours.find("Design Center Hours") != -1:
                hours = hours.split("Design Center Hours")[1].strip()
            if hours.find("For Delivery") != -1:
                hours = hours.split("For Delivery")[0].strip()
            city = a.get("city")
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            if street_address.find("Chadds Ford") != -1:
                ad = street_address
                street_address = " ".join(ad.split()[:3]).strip()
                city = " ".join(ad.split()[3:]).strip()
            store = []
            store.append("https://www.ethanallen.com")
            store.append("https://www.ethanallen.com/en_US/store-locator")
            store.append(name)
            store.append(street_address)
            store.append(city)
            store.append(a.get("state"))
            store.append(a.get("postal") or "<MISSING>")
            store.append("US")
            store.append(store_id)
            store.append(phone if phone != "" else "<MISSING>")
            store.append("ethan allen")
            store.append(location["data-lat"])
            store.append(location["data-lng"])
            store.append(hours)
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
