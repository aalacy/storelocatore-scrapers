import csv
import datetime
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("choicehotels_com__quality-inn")

session = SgRequests()


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
    main_url = "https://choicehotels.com/quality-inn"
    brand_id = "QI"
    locs = []
    today = datetime.date.today().strftime("%Y-%m-%d")
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    addresses = []
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        max_search_results=None,
    )
    for lat, lng in search:
        try:
            x = lat
            y = lng
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
                "Origin": "https://www.choicehotels.com",
                "content-type": "application/x-www-form-urlencoded",
                "cookie": "",
            }
            data = (
                "adults=1&checkInDate="
                + str(today)
                + "&checkOutDate="
                + str(tomorrow)
                + "&lat="
                + str(x)
                + "&lon="
                + str(y)
                + "&minors=0&optimizeResponse=image_url&platformType=DESKTOP&preferredLocaleCode=en-us&ratePlanCode=RACK&ratePlans=RACK%2CPREPD%2CPROMO%2CFENCD&rateType=LOW_ALL&rooms=1&searchRadius=100&siteName=us&siteOpRelevanceSortMethod=ALGORITHM_B"
            )
            r = session.post(
                "https://www.choicehotels.com/webapi/location/hotels",
                headers=headers,
                data=data,
            )

            data = r.json()["hotels"]
            for store_data in data:
                if (
                    store_data["address"]["country"] != "US"
                    and store_data["address"]["country"] != "CA"
                ):
                    continue
                if store_data["brandCode"] != brand_id:
                    continue
                store = []
                store.append(main_url)
                store.append(store_data["name"])
                address = ""
                if "line1" in store_data["address"]:
                    address = address + store_data["address"]["line1"]
                if "line2" in store_data["address"]:
                    address = address + store_data["address"]["line2"]
                if "line3" in store_data["address"]:
                    address = address + store_data["address"]["line3"]
                store.append(address)
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(
                    store_data["address"]["city"]
                    if store_data["address"]["city"]
                    else "<MISSING>"
                )
                store.append(
                    store_data["address"]["subdivision"]
                    if store_data["address"]["subdivision"]
                    else "<MISSING>"
                )
                store.append(
                    store_data["address"]["postalCode"]
                    if store_data["address"]["postalCode"]
                    else "<MISSING>"
                )
                if len(store[-1]) == 10:
                    store[-1] = store[-1][:5] + "-" + store[-1][6:]
                store.append(store_data["address"]["country"])
                store.append("<MISSING>")
                try:
                    store.append(
                        store_data["phone"] if store_data["phone"] else "<MISSING>"
                    )
                except:
                    store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(store_data["lat"])
                store.append(store_data["lon"])
                store.append("<MISSING>")
                store.append("https://www.choicehotels.com/" + str(store_data["id"]))
                ll = str(store_data["lat"]) + "|" + str(store_data["lon"])
                if ll not in locs:
                    yield store
        except:
            pass
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_search_distance_miles=100,
        max_search_results=None,
    )
    for lat, lng in search:
        try:
            x = lat
            y = lng
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
                "Origin": "https://www.choicehotels.com",
                "content-type": "application/x-www-form-urlencoded",
                "cookie": "",
            }
            data = (
                "adults=1&checkInDate="
                + str(today)
                + "&checkOutDate="
                + str(tomorrow)
                + "&lat="
                + str(x)
                + "&lon="
                + str(y)
                + "&minors=0&optimizeResponse=image_url&platformType=DESKTOP&preferredLocaleCode=en-us&ratePlanCode=RACK&ratePlans=RACK%2CPREPD%2CPROMO%2CFENCD&rateType=LOW_ALL&rooms=1&searchRadius=100&siteName=us&siteOpRelevanceSortMethod=ALGORITHM_B"
            )
            r = session.post(
                "https://www.choicehotels.com/webapi/location/hotels",
                headers=headers,
                data=data,
            )

            data = r.json()["hotels"]
            for store_data in data:
                if (
                    store_data["address"]["country"] != "US"
                    and store_data["address"]["country"] != "CA"
                ):
                    continue
                if store_data["brandCode"] != brand_id:
                    continue
                store = []
                store.append(main_url)
                store.append(store_data["name"])
                address = ""
                if "line1" in store_data["address"]:
                    address = address + store_data["address"]["line1"]
                if "line2" in store_data["address"]:
                    address = address + store_data["address"]["line2"]
                if "line3" in store_data["address"]:
                    address = address + store_data["address"]["line3"]
                store.append(address)
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(
                    store_data["address"]["city"]
                    if store_data["address"]["city"]
                    else "<MISSING>"
                )
                store.append(
                    store_data["address"]["subdivision"]
                    if store_data["address"]["subdivision"]
                    else "<MISSING>"
                )
                store.append(
                    store_data["address"]["postalCode"]
                    if store_data["address"]["postalCode"]
                    else "<MISSING>"
                )
                if len(store[-1]) == 10:
                    store[-1] = store[-1][:5] + "-" + store[-1][6:]
                store.append(store_data["address"]["country"])
                store.append("<MISSING>")
                try:
                    store.append(
                        store_data["phone"] if store_data["phone"] else "<MISSING>"
                    )
                except:
                    store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(store_data["lat"])
                store.append(store_data["lon"])
                store.append("<MISSING>")
                store.append("https://www.choicehotels.com/" + str(store_data["id"]))
                ll = str(store_data["lat"]) + "|" + str(store_data["lon"])
                if ll not in locs:
                    yield store
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
