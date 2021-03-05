import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

log = SgLogSetup().get_logger("comforcare.com")


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []
    locator_domain = "comforcare.com"

    for state in states:
        log.info(state)
        link = (
            "https://www.comforcare.com/ajax.Location.php?action=locations&zipcode=&state="
            + state
        )
        stores = session.get(link, headers=headers).json()[0]

        for store in stores:
            link = "https://www.comforcare.com/" + store["webaddress"]
            location_name = store["companyname"]
            street_address = (
                store["address1"] + " " + store["address2"] + " " + store["address3"]
            ).strip()
            city = store["city"]
            state = store["state"]
            zip_code = store["zip"]
            country_code = "US"
            store_number = store["id"]
            location_type = "<MISSING>"
            phone = store["phonenumber"]
            if not phone:
                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                phone = base.find(class_="location__phone").a.text.strip()
            hours_of_operation = "<MISSING>"
            latitude = store["latitude"]
            longitude = store["longitude"]

            if not latitude:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

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

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
