import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("anixter_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    base_url = "https://www.anixter.com"
    addresses = []
    US_states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
    for state in US_states:
        json_data = session.get(
            "https://www.anixter.com/en_us/pos/region?searchCode=US-"
            + str(state)
            + "&brand=anixter",
            headers=headers,
        ).json()
        for data in json_data:
            location_name = data["address"]["department"]
            street_address = (
                (data["address"]["line1"] + " " + str(data["address"]["line2"]))
                .replace("None", "")
                .strip()
                .capitalize()
            )
            city = data["address"]["town"]
            state = data["address"]["region"]["isocodeShort"]
            zipp = data["address"]["postalCode"]
            country_code = data["address"]["region"]["countryIso"]
            phone = data["address"]["phone"]
            latitude = data["geoPoint"]["latitude"]
            longitude = data["geoPoint"]["longitude"]
            if latitude == 0.0:
                latitude = "<MISSING>"
            if longitude == 0.0:
                longitude = "<MISSING>"

            page_url = "https://www.anixter.com/en_us" + data["address"]["url"]
            if data["openingHours"] is not None:
                hours_of_operation = (
                    data["openingHours"]["name"] + " " + "Sun-Sat : Closed"
                )
            else:
                hours_of_operation = "<MISSING>"
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            yield store
    addresses1 = []
    US_states = [
        "NL",
        "PE",
        "NS",
        "NB",
        "QC",
        "ON",
        "MB",
        "SK",
        "AB",
        "BC",
        "YT",
        "NT",
        "NU",
    ]
    for state in US_states:
        json_data = session.get(
            "https://www.anixter.com/en_us/pos/region?searchCode=CA-"
            + str(state)
            + "&brand=anixter",
            headers=headers,
        ).json()
        for data in json_data:
            location_name = data["address"]["department"]
            street_address = (
                (data["address"]["line1"] + " " + str(data["address"]["line2"]))
                .replace("None", "")
                .strip()
                .capitalize()
            )
            city = data["address"]["town"]
            if "QUéBEC" == city:
                city = "QUEBEC"
            state = data["address"]["region"]["isocodeShort"]
            zipp = data["address"]["postalCode"]
            country_code = data["address"]["region"]["countryIso"]
            phone = data["address"]["phone"]
            latitude = data["geoPoint"]["latitude"]
            longitude = data["geoPoint"]["longitude"]
            if latitude == 0.0:
                latitude = "<MISSING>"
            if longitude == 0.0:
                longitude = "<MISSING>"
            page_url = "https://www.anixter.com/en_us" + data["address"]["url"]
            if data["openingHours"] is not None:
                hours_of_operation = (
                    data["openingHours"]["name"] + " " + "Sun-Sat : Closed"
                )
            else:
                hours_of_operation = "<MISSING>"
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            if store[-1] in addresses1:
                continue
            addresses1.append(store[-1])
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
