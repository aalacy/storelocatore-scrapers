import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from uszipcode import SearchEngine
import usaddress as usd
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tedbaker_com")
session = SgRequests()
search = SearchEngine(simple_zipcode=True)

tm = {
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
    "BuildingName": "address1",
    "CornerOf": "address1",
    "IntersectionSeparator": "address1",
    "SecondStreetName": "address1",
    "SecondStreetNamePostType": "address1",
    "LandmarkName": "address1",
    "USPSBoxGroupID": "address1",
    "USPSBoxGroupType": "address1",
    "OccupancyType": "address1",
    "OccupancyIdentifier": "address1",
    "SubaddressIdentifier": "address1",
    "SubaddressType": "address1",
    "SubaddressIdentifier": "address1",
    "PlaceName": "city",
    "StateName": "state",
    "ZipCode": "zip_code",
    "Recipient": "recipient",
}


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )

        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    json_data = session.get(
        "https://www.tedbaker.com/us/json/stores/for-country?isocode=US",
        headers=headers,
    )
    data = json_data.json()["data"]
    for i in range(len(data)):
        addr = ""
        store_data = data[i]
        address = store_data["address"]

        try:
            try:
                zipp = address["postalCode"].strip()
                if address["postalCode"] == "-":
                    zipp = address["town"]
            except:
                zipp = store_data["address"]["line3"]
                if "Malibu" in zipp:
                    zipp = address["town"]
        except:
            continue
        zipp = zipp.split(" ")[-1].replace("1091", "10917").replace("HONOLULU", "96814")
        zipcode = search.by_zipcode(zipp)
        city = zipcode.major_city
        state = zipcode.state

        if "line1" in address:
            addr = addr + address["line1"] + " "
        if "line2" in address:
            addr = addr + address["line2"] + " "
        if "line3" in address:
            addr = addr + address["line3"].title() + " "

        raw_add = (
            addr.replace("Santa Monica California", "")
            .replace("Costa Mesa", "")
            .replace("Virginia", "")
            .replace("Florida", "")
            .replace("The Plaza at King of Prussia", "")
            .replace("Nevada", "")
            .replace("Miami Beach", "")
            .replace("Central Valley", "")
            .replace("Texas", "")
            .replace("NorthPark Center,", "")
            .replace("Sawgrass Mills Outlets,", "")
            .replace("Fashion Square,", "")
            .replace("California", "")
        )

        try:
            addr_format = usd.tag(raw_add, tm)
            raw_data = list(addr_format[0].items())

        except usd.RepeatedLabelError:
            street_address = raw_add
        store_number = store_data["name"]

        page_url = "https://www.tedbaker.com/us/stores/store/" + store_number

        if raw_data[0][0] != "recipient":
            street_address = raw_data[0][1].replace(
                "Suite 1a 180", "Suite 1a,180 El Camino Real"
            )
        else:
            street_address = raw_data[1][1].replace(
                "4200 Conroy Rd", "4200 Conroy Rd Space H-232"
            )

        store = []
        store.append("https://www.tedbaker.com")
        store.append(store_data["displayName"])
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number.replace("US", ""))
        store.append(
            store_data["address"]["phone"].lstrip("001-").lstrip("+1").strip()
            if "phone" in store_data["address"]
            and store_data["address"]["phone"] != ""
            and store_data["address"]["phone"] is not None
            else "<MISSING>"
        )
        store.append("Ted Baker")
        store.append(store_data["geoPoint"]["latitude"])
        store.append(store_data["geoPoint"]["longitude"])
        hours = ""
        if "openingHours" in store_data:
            store_hours = store_data["openingHours"]["weekDayOpeningList"]
            for k in range(len(store_hours)):
                if store_hours[k]["closed"] is True:
                    hours = hours + " closed " + store_hours[k]["weekDay"]
                else:
                    hours = (
                        hours
                        + " "
                        + store_hours[k]["weekDay"]
                        + " "
                        + store_hours[k]["openingTime"]["formattedHour"]
                        + " - "
                        + store_hours[k]["closingTime"]["formattedHour"]
                    )
        store.append(hours if hours != "" else "<MISSING>")
        store.append(page_url)
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = store[i].replace("–", "-")
        yield store

    json_data2 = session.get(
        "https://www.tedbaker.com/us/json/stores/for-country?isocode=CA",
        headers=headers,
    )
    data2 = json_data2.json()["data"]
    for i in range(len(data2)):
        addr = ""
        store_data = data2[i]
        address = store_data["address"]
        try:
            if len(address["postalCode"].split(" ")) == 3:
                zipp = " ".join(address["postalCode"].split(" ")[1:])
            else:
                zipp = address["postalCode"]
        except KeyError:
            zipp = " ".join(store_data["address"]["line3"].split(" ")[2:])
        store_number = store_data["name"]
        page_url = "https://www.tedbaker.com/us/stores/store/" + store_number
        r = session.get(page_url)
        soup = BeautifulSoup(r.text, "lxml")
        addr = list(soup.find("ul", {"id": "store_contact_details"}).stripped_strings)
        try:
            addr.remove(",")
            addr.remove("Ted Baker")
            addr.remove("Hudson’s Bay Queen Street")
        except:
            pass
        try:
            addr.remove("Ted Baker Concession")
        except:
            pass
        try:
            addr.remove("Eaton Centre")
        except:
            pass

        phone = addr[-1].replace("001-", "").replace("ext 6055", "")
        addr.pop(-1)
        if zipp in addr:
            addr.pop(-1)

        if len(addr) == 4:
            street_address = " ".join(addr[:2])
            if "Ted Baker" in street_address:
                street_address = (
                    "Unit 329A, Rideau Centre - 3rd level, 50 Rideau Street"
                )
            city = (
                addr[2]
                .replace("Ontario", "Halton Hills")
                .replace("50 Rideau Street", "Ottawa")
            )
            state = (
                addr[-1]
                .replace("Canada", "")
                .replace(zipp, "")
                .replace("Ottawa", "<MISSING>")
                .replace("Halton Hills", "Ontario")
                .strip()
            )
        else:
            street_address = (
                " ".join(addr[:2])
                .replace("VANCOUVER", "")
                .replace("Hudson’s Bay Queen Street", "")
                .strip()
            )
            city = addr[-1].split(" ")[0].replace("BC", "VANCOUVER").strip(",")
            try:
                state = addr[-1].split(" ")[1].replace("V6C", "BC").strip()
            except:
                state = "ON"

        store = []
        store.append("https://www.tedbaker.com")
        store.append(store_data["displayName"])
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("CA")
        store.append(store_number.replace("CA", "").replace("B", ""))
        store.append(phone.replace("+1604", "604"))
        store.append("Ted Baker")
        store.append(store_data["geoPoint"]["latitude"])
        store.append(store_data["geoPoint"]["longitude"])
        hours = ""
        if "openingHours" in store_data:
            store_hours = store_data["openingHours"]["weekDayOpeningList"]
            for k in range(len(store_hours)):
                if store_hours[k]["closed"] is True:
                    hours = hours + " closed " + store_hours[k]["weekDay"]
                else:
                    hours = (
                        hours
                        + " "
                        + store_hours[k]["weekDay"]
                        + " "
                        + store_hours[k]["openingTime"]["formattedHour"]
                        + " - "
                        + store_hours[k]["closingTime"]["formattedHour"]
                    )
        store.append(hours if hours != "" else "<MISSING>")
        store.append(page_url)
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = store[i].replace("–", "-")
                store[i] = store[i].replace("’", "'")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
