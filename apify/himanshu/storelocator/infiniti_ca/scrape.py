import csv
from concurrent.futures import ThreadPoolExecutor
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from sgrequests import SgRequests

logger = SgLogSetup().get_logger("infiniti_ca")
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


def get_url(data):

    headers = {
        "Accept": "*/*",
        "clientKey": "lVqTrQx76FnGUhV6AFi7iSy9aXRwLIy7",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "apiKey": "mKvJTEihQ3gYy0GhoYKWrAbKfzWt3PsE",
    }

    data = session.get(data, headers=headers)
    try:
        return data
    except:
        pass


def _send_multiple_rq(vk):
    with ThreadPoolExecutor(max_workers=len(vk)) as pool:
        return list(pool.map(get_url, vk))


def fetch_data():
    addresses = []
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=50,
        max_search_results=200,
    )
    list_of_urls = []

    for coord in search:
        list_of_urls.append(
            "https://us.nissan-api.net/v2/dealers?size=50&isMarketingDealer=true&location="
            + str(coord)
            + "&serviceFilterType=AND&include=openingHours"
        )

    data = _send_multiple_rq(list_of_urls)
    for q in data:
        r1 = q.json()
        if "dealers" in r1:
            locator_domain = "https://www.infiniti.ca/"
            location_name = ""
            zipp = ""
            country_code = "US"
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            hours_of_operation = ""
            for location in r1["dealers"]:
                storeNumber = "<MISSING>"
                location_name = location["name"]
                phone = location["contact"]["phone"]
                storeNumber = "<MISSING>"
                latitude = location["geolocation"]["latitude"]
                longitude = location["geolocation"]["longitude"]
                zipp = location["address"]["postalCode"]
                if zipp.replace("-", "").strip().isdigit():
                    country_code = "US"
                else:
                    country_code = "CA"
                if phone.strip().lstrip():
                    phone = phone
                else:
                    phone = "<MISSING>"
                try:
                    page_url = location["contact"]["websites"][0]["url"]
                except:
                    page_url = ""
                hours_of_operation = ""
                day = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                for h in location["openingHours"]["regularOpeningHours"]:
                    if "openIntervals" in h:
                        weekDay = day[h["weekDay"] - 1]
                        for q in h["openIntervals"]:
                            hours_of_operation += (
                                " "
                                + weekDay
                                + " open "
                                + q["openFrom"]
                                + " colse "
                                + q["openUntil"]
                            )
                    else:
                        weekDay = day[h["weekDay"] - 1]
                        hours_of_operation += (
                            " " + day[h["weekDay"] - 1] + " " + "closed"
                        )

                store = [
                    locator_domain,
                    location_name,
                    location["address"]["addressLine1"],
                    location["address"]["city"].capitalize(),
                    location["address"]["state"],
                    zipp,
                    country_code,
                    storeNumber,
                    phone.strip(),
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                    page_url.lower(),
                ]

                if str(store[2]) in addresses:
                    continue
                addresses.append(str(store[2]))
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
