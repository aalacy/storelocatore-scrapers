import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_distance_miles=49,
        max_search_results=50,
    )
    return_main_object = []
    addresses = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    app_key_request = session.get(
        "https://hosted.where2getit.com/northface/2015/index.html"
    )
    app_key_soup = BeautifulSoup(app_key_request.text, "html.parser")
    app_key = "C1907EFA-14E9-11DF-8215-BBFCBD236D0E"
    for script in app_key_soup.find_all("script"):
        if "appkey: " in script.text:
            app_key = script.text.split("appkey: ")[1].split(",")[0].replace("'", "")
    for zip_code in search:

        data = (
            '{"request":{"appkey":"'
            + app_key
            + '","formdata":{"geoip":false,"dataview":"store_default","limit":1000,"order":"rank, _DISTANCE","geolocs":{"geoloc":[{"addressline":"'
            + str(zip_code)
            + '","country":"US","latitude":"","longitude":""}]},"searchradius":"100","where":{"visiblelocations":{"eq":""},"or":{"northface":{"eq":""},"outletstore":{"eq":""},"retailstore":{"eq":""},"summit":{"eq":""}},"and":{"youth":{"eq":""},"apparel":{"eq":""},"footwear":{"eq":""},"equipment":{"eq":""},"mt":{"eq":""},"access_pack":{"eq":""},"steep_series":{"eq":""}}},"false":"0"}}}'
        )
        r = session.post(
            "https://hosted.where2getit.com/northface/2015/rest/locatorsearch?lang=en_EN",
            headers=headers,
            data=data,
        )
        if "collectioncount" not in r.json()["response"]:
            continue
        for store_data in r.json()["response"]["collection"]:
            store = ["https://www.thenorthface.com"]
            page_url = "https://www.thenorthface.com/utility/store-locator.html"
            if store_data["country"] == "CA":
                page_url = (
                    "https://www.thenorthface.com/en_ca/utility/store-locator.html"
                )
            storekey = store_data["clientkey"]
            if storekey and "USA" in "".join(storekey):
                page_url = (
                    "https://stores.thenorthface.com/"
                    + "".join(store_data["state"]).lower()
                    + "/"
                    + "".join(store_data["city"]).replace(" ", "-").lower()
                    + "/"
                    + storekey
                )
            store.append(page_url)
            location_name = store_data["name"]
            store.append(location_name)
            address = ""
            if store_data["address1"] is not None:
                address = address + store_data["address1"]
            if store_data["address2"] is not None:
                address = address + store_data["address2"]
            if address == "":
                continue
            store.append(address)
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(
                store_data["city"]
                if store_data["city"] != "" and store_data["city"] is not None
                else "<MISSING>"
            )
            store.append(
                store_data["state"]
                if store_data["country"] == "US"
                else store_data["province"]
            )
            if store[-1] is None:
                store[-1] = "<MISSING>"
            location_type = "the north face"
            north_store = store_data.get("northface")
            if north_store == "1":
                location_type = "the north face store"
            outlet_store = store_data.get("outletstore")
            if outlet_store == "1":
                location_type = "the north face outletstore"
            store.append(
                store_data["postalcode"]
                if store_data["postalcode"] != ""
                and store_data["postalcode"] is not None
                else "<MISSING>"
            )
            store.append(store_data["country"])
            store.append(
                store_data["storenumber"]
                if store_data["storenumber"] is not None
                else "<MISSING>"
            )
            store.append(
                store_data["phone"].split("or")[0].split(";")[0].split("and")[0]
                if store_data["phone"] is not None and store_data["phone"] != "TBD"
                else "<MISSING>"
            )
            store.append(location_type)
            store.append(
                store_data["latitude"]
                if store_data["latitude"] != "" and store_data["latitude"] is not None
                else "<MISSING>"
            )
            store.append(
                store_data["longitude"]
                if store_data["longitude"] != "" and store_data["longitude"] is not None
                else "<MISSING>"
            )
            hours = ""
            if store_data["m"] is not None:
                hours = hours + " Monday " + store_data["m"]
            if store_data["t"] is not None:
                hours = hours + " Tuesday " + store_data["t"]
            if store_data["w"] is not None:
                hours = hours + " Wednesday " + store_data["w"]
            if store_data["thu"] is not None:
                hours = hours + " Thursday " + store_data["thu"]
            if store_data["f"] is not None:
                hours = hours + " Friday " + store_data["f"]
            if store_data["sa"] is not None:
                hours = hours + " Saturday " + store_data["sa"]
            if store_data["su"] is not None:
                hours = hours + " Sunday " + store_data["su"]
            store.append(hours if hours != "" else "<MISSING>")

            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
