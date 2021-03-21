import csv

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("ashleyfurniture_com")


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

    us_state_abbrev = {
        "Alabama": "AL",
        "Alaska": "AK",
        "American Samoa": "AS",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "District of Columbia": "DC",
        "Florida": "FL",
        "Georgia": "GA",
        "Guam": "GU",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Northern Mariana Islands": "MP",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Puerto Rico": "PR",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virgin Islands": "VI",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
        "Alberta": "AB",
        "British Columbia": "BC",
        "Manitoba": "MB",
        "New Brunswick": "NB",
        "Nova Scotia": "NS",
        "Nunavut": "NU",
        "Newfoundland and Labrador": "NL",
        "Ontario": "ON",
        "Northwest Territories": "NT",
        "Prince Edward Island": "PE",
        "Quebec": "QC",
        "Saskatchewan": "SK",
        "Yukon": "YT",
    }

    abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))
    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "ashleyfurniture.com"

    all_store_data = []

    base_link = "https://stores.ashleyfurniture.com/umbraco/surface/location/GetDataByState?region="

    for st in abbrev_us_state:
        api_link = base_link + st
        logger.info(api_link)
        stores = session.get(api_link, headers=headers).json()["StoreLocations"]

        for store in stores:

            raw_address = store["ExtraData"]["Address"]
            try:
                street_address = (
                    raw_address["AddressNonStruct_Line1"]
                    + " "
                    + raw_address["AddressNonStruct_Line2"]
                ).strip()
            except:
                street_address = raw_address["AddressNonStruct_Line1"].strip()

            city = raw_address["Locality"]
            if city == "Guatemala":
                continue
            state = raw_address["Region"]
            zip_code = raw_address["PostalCode"]
            country_code = raw_address["CountryCode"]
            if country_code not in ["US", "CA"]:
                continue

            location_name = store["Name"] + " " + city
            store_number = store["LocationNumber"]

            link = (
                "https://stores.ashleyfurniture.com/store/"
                + country_code.lower()
                + "/"
                + abbrev_us_state[st].lower().replace(" ", "-")
                + "/"
                + city.lower().replace(" ", "-")
                + "/"
                + store_number
            )
            phone = store["ExtraData"]["Phone"]
            location_type = "<MISSING>"

            hours_of_operation = ""
            try:
                raw_hours = store["ExtraData"]["HoursOfOpStruct"]
                for day in raw_hours:
                    if day == "SpecialHours":
                        continue

                    try:
                        day_hours = (
                            raw_hours[day]["Ranges"][0]["StartTime"]
                            + "-"
                            + raw_hours[day]["Ranges"][0]["EndTime"]
                        )
                    except:
                        day_hours = "Closed"

                    hours_of_operation = (
                        hours_of_operation + " " + day + " " + day_hours
                    ).strip()
            except:
                try:
                    hours_of_operation = ""
                    days = ["Su ", "Mo ", "Tu ", "We ", "Th ", "Fr ", "Sa "]
                    raw_hours = store["ExtraData"]["CustomerServiceHours"].split(",")
                    for i, day in enumerate(days):
                        hours_of_operation = (
                            hours_of_operation + " " + day + raw_hours[i]
                        ).strip()
                except:
                    hours_of_operation = "<MISSING>"

            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            latitude = store["Location"]["coordinates"][1]
            longitude = store["Location"]["coordinates"][0]

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
