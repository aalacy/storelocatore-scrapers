import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("sherwin-williams_com")

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


def clean(x):
    return x.replace("&#039;", "'").replace("amp;", "")


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    r = session.get("https://www.sherwin-williams.com/store-locator", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    location_types = []
    for option in soup.find("select", {"id": "findstores_selectStoreType"}).find_all(
        "option"
    ):
        location_types.append(option["value"])
    store_id = soup.find("meta", {"name": "CommerceSearch"})["content"].split("_")[-1]
    for script in soup.find_all("script"):
        if "WCParamJS " in str(script):
            catalog_id = (
                str(script)
                .split("catalogId")[1]
                .split(",")[0]
                .replace("'", "")
                .replace('"', "")
                .replace(":", "")
            )
    addresses = []
    max_results = 25
    max_distance = 75
    r_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
    }
    for loc_type in location_types:

        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
            max_search_distance_miles=max_distance,
            max_search_results=max_results,
        )
        logger.info("Sgzips for loc_type: %s" % loc_type)

        for x, y in search:
            r_data = (
                "sideBarType=LSTORES&latitude="
                + str(x)
                + "&longitude="
                + str(y)
                + "&radius=75&uom=SMI&abbrv=us&storeType="
                + loc_type
                + "&countryCode=&requesttype=ajax&langId=&storeId="
                + str(store_id)
                + "&catalogId="
                + str(catalog_id)
            )
            r = session.post(
                "https://www.sherwin-williams.com/AjaxStoreLocatorSideBarView?langId=-1&storeId="
                + str(store_id),
                headers=r_headers,
                data=r_data,
            )
            soup = BeautifulSoup(r.text, "lxml")
            data = json.loads(
                soup.find("script", {"id": "storeResultsJSON"}).contents[0]
            )["stores"]
            for store_data in data:
                lat = store_data["latitude"]
                lng = store_data["longitude"]
                search.found_location_at(lat, lng)
                store = []
                store.append("https://www.sherwin-williams.com")
                store.append(clean(store_data["name"]))
                store.append(clean(store_data["address"]))
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(clean(store_data["city"]))
                store.append(store_data["state"])
                store_data["zipcode"] = store_data["zipcode"].replace(
                    "                                   ", ""
                )
                if store_data["zipcode"].replace(" ", "").replace("-", "").isdigit():
                    store.append(store_data["zipcode"].replace(" ", ""))
                    store.append("US")
                else:
                    ca_zip = store_data["zipcode"].replace(" ", "")
                    store.append(ca_zip[:3] + " " + ca_zip[3:])
                    store.append("CA")
                store_num = store_data["url"].split("storeNumber=")[1].split("&")[0]
                if store_num in [
                    "190520",
                    "24921",
                    "627001",
                    "622001",
                    "614502",
                    "621001",
                ]:
                    continue
                store.append(store_num)
                store.append(
                    store_data["phone"].replace("  ", "")
                    if "phone" in store_data
                    and store_data["phone"] != ""
                    and store_data["phone"] is not None
                    else "<MISSING>"
                )
                store.append(loc_type)
                store.append(lat)
                store.append(lng)
                link = "https://www.sherwin-williams.com" + store_data["url"]
                location_request = session.get(
                    link,
                    headers=headers,
                )
                location_soup = BeautifulSoup(location_request.text, "lxml")

                hours = ""
                try:
                    hours = (
                        " ".join(
                            list(
                                location_soup.find(
                                    "div",
                                    {
                                        "class": "cmp-storedetailhero__store-hours-container"
                                    },
                                ).stripped_strings
                            )
                        )
                        .replace("Store Hours", "")
                        .strip()
                    )
                except:
                    pass
                store.append(hours if hours != "" else "<MISSING>")
                store.append(link)
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
