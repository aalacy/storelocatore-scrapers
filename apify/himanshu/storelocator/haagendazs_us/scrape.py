from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("haagendazs_us")
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
    addresses = []
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=200,
    )
    MAX_DISTANCE = 50
    for lat, lng in search:
        result_coords = []
        lat = str(lat)
        lng = str(lng)

        locator_domain = "https://www.haagendazs.us"
        location_name = "<MISSING>"
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zipp = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"
        page_url = "<MISSING>"
        try:
            json_data = session.get(
                "https://www.haagendazs.us/locator/ws/"
                + str(search.current_zip)
                + "/"
                + lat
                + "/"
                + lng
                + "/25/0/2452?lat="
                + lat
                + "&lon="
                + lng
                + "&radius="
                + str(MAX_DISTANCE)
                + "&zipcode="
                + str(search.current_zip)
                + "&BrandFlavorID=2452&targetsearch=3"
            ).json()
        except:
            continue
        for data in json_data:
            url = data["URL"].strip()
            if url:
                page_url = "https://www.haagendazs.us" + url
                html = session.get(page_url)
                soup = BeautifulSoup(html.text, "lxml")
                try:
                    hours_of_operation = " ".join(
                        list(
                            soup.find(
                                "div", attrs={"class": "office-hours"}
                            ).stripped_strings
                        )
                    )
                except:
                    hours_of_operation = ""
            else:
                page_url = "<MISSING>"
                hours_of_operation = "<MISSING>"
            result_coords.append((data["lat__c"], data["lon__c"]))
            location_type = data["IsHDShop"]
            if location_type is True:
                continue
            else:
                location_type = "store"
            store = [
                locator_domain,
                data["Name"].replace("®", "").replace("Ä", "A"),
                data["Shop_Street__c"],
                data["Shop_City__c"],
                data["Shop_State_Province__c"],
                data["Shop_Zip_Postal_Code__c"],
                country_code,
                store_number,
                data["phone"],
                location_type,
                data["lat__c"],
                data["lon__c"],
                hours_of_operation,
                page_url,
            ]
            store = [
                x.replace("\n", "").replace("\t", "") if x else "<MISSING>"
                for x in store
            ]
            store = [
                str(x).encode("ascii", "ignore").decode("ascii").strip()
                if x
                else "<MISSING>"
                for x in store
            ]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store

    r = session.get("https://www.haagendazs.us/all-shops")
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find("div", {"class": "view-content"}).find_all("a")
    for link in links:
        page_url = "https://www.haagendazs.us/" + link["href"]
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        location_name = soup1.find("h1", {"itemprop": "name"}).text.strip()
        street_address = soup1.find("p", {"itemprop": "streetAddress"}).text.strip()
        city = soup1.find("span", {"itemprop": "addressLocality"}).text.strip()
        state = soup1.find("span", {"itemprop": "addressRegion"}).text.strip()
        zipp = (
            soup1.find("span", {"itemprop": "addressRegion"})
            .find_next("span")
            .text.strip()
        )
        try:
            latitude = (
                soup1.find(lambda tag: (tag.name == "script") and "lat" in tag.text)
                .text.split('lat:"')[1]
                .split('",')[0]
            )
        except:
            latitude = "<MISSING>"
        try:
            longitude = (
                soup1.find(lambda tag: (tag.name == "script") and "lat" in tag.text)
                .text.split('long:"')[1]
                .split('",')[0]
            )
        except:
            longitude = "<MISSING>"
        if soup1.find("div", {"class": "office-hours"}):
            hours = " ".join(
                list(soup1.find("div", {"class": "office-hours"}).stripped_strings)
            )
        else:
            hours = "<MISSING>"

        store = []
        store.append("https://www.haagendazs.us")
        store.append(location_name.replace("®", "").replace("Ä", "A"))
        store.append(street_address.replace("\n", "").replace("\t", ""))
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("Shop")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        store = [x.strip() if isinstance(x, str) else x for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
