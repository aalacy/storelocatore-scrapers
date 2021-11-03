import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("bancorpsouth.com")


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


def fetch_data():

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
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

    session = SgRequests()

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Host": "www.bancorpsouth.com",
        "Origin": "https://www.bancorpsouth.com",
        "Referer": "https://www.bancorpsouth.com/find-a-location",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    }

    locator_domain = "bancorpsouth.com"

    all_store_data = []

    base_link = "https://www.bancorpsouth.com/SiteServices/BranchLocatorSearch"

    for st in states:
        logger.info(st)
        payload = {"Location": st, "LocationType": "2"}

        stores = session.post(base_link, headers=headers, json=payload).json()[
            "results"
        ]

        for store in stores:

            link = "https://www.bancorpsouth.com" + store["link"]
            location_name = store["branchName"]

            if not store["isATM"]:
                continue

            street_address = store["street1"]
            city = store["city"]
            state = store["state"]
            zip_code = store["zip"]
            country_code = "US"

            store_number = "<MISSING>"
            phone = store["phone"].split("or")[0].strip()
            if not phone:
                phone = "<MISSING>"

            hours_of_operation = (
                " ".join(list(BeautifulSoup(store["hours"], "lxml").stripped_strings))
                .split("AT THIS TIME")[0]
                .strip()
            )
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
            latitude = store["latitude"]
            longitude = store["longitude"]

            if "atm" in location_name.lower():
                location_type = "ATM"
            else:
                location_type = "ATM, Branch"

            all_store_data.append(
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

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
