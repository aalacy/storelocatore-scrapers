import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgzip.dynamic import SearchableCountries

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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }

    # base_url = "https://www.bmw.com/"
    # r = session.get("https://www.bmwusa.com/api/dealers/41501/1000", headers=headers)
    # for store_data in r.json()["Dealers"]:
    #     store = []
    #     store.append(base_url)
    #     store.append(store_data["DefaultService"]["Name"])
    #     store.append(store_data["DefaultService"]["Address"])
    #     if store[-1] in addresses:
    #         continue
    #     addresses.append(store[-1])
    #     store.append(store_data["DefaultService"]["City"])
    #     store.append(store_data["DefaultService"]["State"])
    #     store.append(store_data["DefaultService"]["ZipCode"])
    #     store.append("US")
    #     store.append(store_data["CenterId"])
    #     store.append(
    #         store_data["DefaultService"]["FormattedPhone"]
    #         if store_data["DefaultService"]["FormattedPhone"] != ""
    #         and store_data["DefaultService"]["FormattedPhone"] is not None
    #         else "<MISSING>"
    #     )
    #     store.append("bmw us")
    #     store.append(store_data["DefaultService"]["LonLat"]["Lat"])
    #     store.append(store_data["DefaultService"]["LonLat"]["Lon"])
    #     hours = " ".join(
    #         list(
    #             BeautifulSoup(
    #                 store_data["DefaultService"]["FormattedHours"], "lxml"
    #             ).stripped_strings
    #         )
    #     )
    #     store.append(hours if hours != "" else "<MISSING>")
    #     store.append("<MISSING>")
    #     logger.info(store)
    #     yield store

    countries = SearchableCountries.WITH_COORDS_ONLY
    countries.extend(SearchableCountries.WITH_ZIPCODE_AND_COORDS)
    countries.sort()

    for i in countries:
        country = i.upper()
        if country in addresses:
            continue
        addresses.append(country)

        r1 = session.get(
            "https://c2b-services.bmw.com/c2b-localsearch/services/api/v4/clients/BMWSTAGE2_DLO/%s/pois?brand=BMW_BMWM&cached=off&callback=angular.callbacks._0&category=BM&country=%s&language=en&lat=0&lng=0&maxResults=2000&showAll=true&unit=km"
            % (country, country),
            headers=headers,
        )
        soup1 = BeautifulSoup(r1.text, "lxml")
        jd = str(soup1).split("angular.callbacks._0(")[1].split(")</p>")[0]
        json_data = json.loads(jd)["data"]["pois"]
        for value in json_data:
            locator_domain = "https://www.bmw.com/"
            location_name = value["name"]
            street_address = value["street"]
            city = value["city"]
            if location_name == "BMW Ste-Agathe":
                state = "QC"
            else:
                state = value["state"]
            if not state:
                state = "<MISSING>"
            zipp = value["postalCode"]
            if not zipp:
                zipp = "<MISSING>"
            country_code = value["countryCode"]
            phone = value["attributes"]["phone"].replace("+1 ", "")
            if not phone:
                phone = "<MISSING>"
            lat = value["lat"]
            lng = value["lat"]
            store_number = value["attributes"]["distributionPartnerId"]

            if location_name + street_address in addresses:
                continue
            addresses.append(location_name + street_address)

            store = []
            store.append(locator_domain)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append("<MISSING>")
            store.append("<MISSING>")
            yield store


def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)


scrape()
