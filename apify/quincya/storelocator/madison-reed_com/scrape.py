import csv
import re
import ssl

from sgrequests import SgRequests

from sgselenium import SgChrome

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    base_link = "https://www.madison-reed.com/colorbar/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).driver()
    driver.get(base_link)

    cookies = driver.get_cookies()
    cookie = ""
    for cook in cookies:
        cookie = cookie + cook["name"] + "=" + cook["value"] + "; "
    cookie = cookie.strip()[:-1]

    csrf = driver.get_cookie("csrf_stp")["value"]

    headers = {
        "authority": "www.madison-reed.com",
        "method": "GET",
        "path": "/api/colorbar/getAllRegions",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "cookie": cookie,
        "sec-ch-ua": 'Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        "sec-ch-ua-mobile": "?0",
        "pragma": "no-cache",
        "referer": "https://www.madison-reed.com/colorbar/locations",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "x-csrf-stp": csrf,
    }

    session = SgRequests()

    api_link = "https://www.madison-reed.com/api/colorbar/getLocationsGroupedByRegion"
    stores = session.get(api_link, headers=headers).json()[0]

    data = []
    locator_domain = "madison-reed.com"

    for state in stores:
        state_stores = stores[state]
        for store in state_stores:
            opened = store["hasOpened"]
            if not opened:
                continue
            location_name = store["neighborhood"]
            street_address = store["address1"].strip()
            if not street_address[:1].isnumeric():
                street_address = store["address2"].strip()
            city = store["city"].strip()
            state = store["state"]
            zip_code = store["zip"]
            country_code = "US"
            store_number = store["_id"]
            location_type = "<MISSING>"
            phone = store["phone"]
            hours = store["hours"]
            hours_of_operation = ""
            for row in hours:
                day = row["day"]
                closed = row["closed"]
                if closed:
                    hours_of_operation = hours_of_operation + " " + day + " Closed"
                else:
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + day
                        + " "
                        + row["open"]
                        + "-"
                        + row["close"]
                    )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
            latitude = store["coordinates"]["lat"]
            longitude = store["coordinates"]["lon"]
            link = "https://www.madison-reed.com/colorbar/locations/" + store["code"]
            # Store data
            data.append(
                [
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
            )
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
