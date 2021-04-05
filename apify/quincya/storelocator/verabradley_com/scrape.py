import csv

from sgrequests import SgRequests


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []
    locator_domain = "verabradley.com"

    us_states = [
        "alabama",
        "alaska",
        "arizona",
        "arkansas",
        "california",
        "colorado",
        "connecticut",
        "delaware",
        "florida",
        "georgia",
        "hawaii",
        "idaho",
        "illinois",
        "indiana",
        "iowa",
        "kansas",
        "kentucky",
        "louisiana",
        "maine",
        "maryland",
        "massachusetts",
        "michigan",
        "minnesota",
        "mississippi",
        "missouri",
        "montana",
        "nebraska",
        "nevada",
        "new hampshire",
        "new jersey",
        "new mexico",
        "new york",
        "north carolina",
        "north dakota",
        "ohio",
        "oklahoma",
        "oregon",
        "pennsylvania",
        "rhode island",
        "south carolina",
        "south dakota",
        "tennessee",
        "texas",
        "utah",
        "vermont",
        "virginia",
        "washington",
        "west virginia",
        "wisconsin",
        "wyoming",
    ]

    for state in us_states:
        base_link = (
            "https://stores.verabradley.com/umbraco/api/location/getlocationsinstate?searchfilter=full,outlet&state="
            + state.title()
        )
        stores = session.get(base_link, headers=headers).json()["Locations"]

        for store in stores:
            store = store["Result"]
            location_name = store["AlternateCorporateName"]
            street_address = (store["Address"] + " " + store["Address2"]).strip()
            city = store["City"]
            state = store["StateABBR"]
            zip_code = store["ZipCode"]
            country_code = "US"
            store_number = store["StoreNumber"]
            if store["StoreType"] == "full":
                location_type = "Retail"
            elif store["StoreType"] == "outlet":
                location_type = "Factory"
            else:
                location_type = store["StoreType"].title()
            phone = store["Phone"]
            hours_of_operation = (
                "Monday "
                + store["MondayHours"]
                + " Tuesday "
                + store["TuesdayHours"]
                + " Wednesday "
                + store["WednesdayHours"]
                + " Thursday "
                + store["ThursdayHours"]
                + " Friday "
                + store["FridayHours"]
                + " Saturday "
                + store["SaturdayHours"]
                + " Sunday "
                + store["SundayHours"]
            ).strip()
            latitude = store["Latitude"]
            longitude = store["Longitude"]
            link = "https://stores.verabradley.com" + store["Url"]

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
