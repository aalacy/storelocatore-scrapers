import csv

from tenacity import retry, stop_after_attempt
from sglogging import sglog
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="morganstanley.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


@retry(stop=stop_after_attempt(3))
def fetch_locations(url, headers, session):
    return session.get(url, headers=headers).json()


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    driver = SgChrome(
        user_agent=user_agent, executable_path="/bin/chromedriver"
    ).driver()

    base_link = "https://advisor.morganstanley.com/search?profile=16348&q=19125&r=2500"

    driver.get(base_link)

    cookies = driver.get_cookies()
    cookie = ""
    for cook in cookies:
        if cook["name"] in ["ak_bmsc", "_ga", "_gid", "_gat_yext"]:
            cookie = cookie + cook["name"] + "=" + cook["value"] + "; "
    cookie = cookie.strip()[:-1]

    if "_gat_yext" not in cookie:
        cookie = cookie + "; _gat_yext=1"

    session = SgRequests()

    found_poi = []

    locator_domain = "morganstanley.com"

    max_results = 600
    max_distance = 2500

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    for postcode in search:
        base_link = (
            "https://advisor.morganstanley.com/search?profile=16348&q=%s&r=%s"
            % (postcode, max_distance)
        )

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Cookie": cookie,
            "Host": "advisor.morganstanley.com",
            "Referer": "https://advisor.morganstanley.com/search?profile=16348&q=%s&r=%s"
            % (postcode, max_distance),
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        }

        log.info(base_link)
        req = fetch_locations(base_link, headers, session)
        stores = req["response"]["entities"]
        count = req["response"]["count"]

        total = int(count / 10) + (count % 10 > 0)
        for page_num in range(1, total + 1):

            for i in stores:
                store = i["profile"]

                try:
                    street_address = (
                        store["address"]["line1"] + " " + store["address"]["line2"]
                    ).strip()
                except TypeError:
                    street_address = store["address"]["line1"].strip()
                city = store["address"]["city"]
                location_name = "Morgan Stanley " + city + " Branch"
                state = store["address"]["region"]
                zip_code = store["address"]["postalCode"]
                country_code = store["address"]["countryCode"]
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                phone = store["mainPhone"]["display"]

                street_city = street_address + city
                if street_city in found_poi:
                    continue
                found_poi.append(street_city)

                hours_of_operation = "<MISSING>"
                latitude = store["yextDisplayCoordinate"]["lat"]
                longitude = store["yextDisplayCoordinate"]["long"]

                try:
                    link = store["websiteUrl"]
                except KeyError:
                    link = "<MISSING>"
                if not link:
                    link = "<MISSING>"

                search.found_location_at(latitude, longitude)

                yield [
                    locator_domain,
                    link,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]

            offset = page_num * 10
            next_link = base_link + "&offset=" + str(offset)
            log.info(next_link)
            stores = fetch_locations(next_link, headers, session)["response"][
                "entities"
            ]
    driver.close()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
