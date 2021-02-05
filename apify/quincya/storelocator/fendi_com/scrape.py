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

    base_links = [
        "https://www.fendi.com/us/store-locator?listJson=true&country-selectize=&fendiType=BOUTIQUE&service=&line=&xlat=25.82&xlng=-124.39&ylat=49.38&ylng=-66.94&country=US",
        "https://www.fendi.com/us/store-locator?listJson=true&country-selectize=&fendiType=BOUTIQUE&service=&line=&xlat=41.631435&xlng=-141.06047&ylat=83.185506&ylng=-52.569408",
        "https://www.fendi.com/us/store-locator?listJson=true&country-selectize=&fendiType=BOUTIQUE&service=&line=&xlat=49.816770000000005&xlng=-8.699566&ylat=60.906456999999996&ylng=1.8129570000000002",
    ]

    session = SgRequests()
    data = []
    found = []

    for base_link in base_links:
        stores = session.get(base_link, headers=headers).json()

        locator_domain = "fendi.com"

        for store in stores:
            location_name = store["displayName"]

            if location_name in found:
                continue
            found.append(location_name)
            try:
                street_address = (
                    store["address"]["line1"] + " " + store["address"]["line2"]
                ).strip()
            except:
                street_address = store["address"]["line1"].strip()
            if ":" in street_address:
                street_address = street_address.split(":")[1].strip()
            if street_address[-1:] == ",":
                street_address = street_address[:-1]
            city = store["address"]["town"]
            try:
                state = store["address"]["region"]["isocodeShort"]
            except:
                state = "<MISSING>"
            zip_code = store["address"]["postalCode"]
            country_code = store["address"]["country"]["isocode"]
            if country_code == "GB":
                state = "<MISSING>"
            store_number = store["name"]
            location_type = "<MISSING>"

            try:
                hours = store["openingHours"]["weekDayOpeningList"]
            except:
                hours_of_operation = "<MISSING>"
            try:
                hours_of_operation = ""
                for hour in hours:
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + hour["weekDay"]
                        + " "
                        + hour["openingHours"]
                    ).strip()
            except:
                hours_of_operation = ""
                for hour in hours:
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + hour["weekDay"]
                        + " "
                        + hour["openingTime"]["formattedHour"]
                        + " "
                        + hour["closingTime"]["formattedHour"]
                    ).strip()

            latitude = store["geoPoint"]["latitude"]
            longitude = store["geoPoint"]["longitude"]
            try:
                phone = store["address"]["phone"]
            except:
                phone = "<MISSING>"
            # Store data
            data.append(
                [
                    locator_domain,
                    "https://www.fendi.com/us/store-locator",
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
