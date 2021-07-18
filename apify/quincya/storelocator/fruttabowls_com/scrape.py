import csv

from sgrequests import SgRequests


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

    base_link = "https://fruttabowls.com/wp-content/themes/munroe-base-camp/templates/blocks/yext/yext-list-get-handler.php?location="

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["response"]["entities"]

    locator_domain = "fruttabowls.com"
    data = []

    for store in stores:
        try:
            street_address = (
                store["address"]["line1"].strip()
                + " "
                + store["address"]["line2"].strip()
            ).strip()
        except:
            street_address = store["address"]["line1"].strip()
        city = store["address"]["city"]
        state = store["address"]["region"]
        zip_code = store["address"]["postalCode"]
        try:
            location_name = "Frutta Bowls - " + store["facebookDescriptor"]
        except:
            location_name = "Frutta Bowls - " + city
        if "Permanently Closed" in store["name"]:
            continue
        if "Coming Soon" in store["featuredMessage"]["description"]:
            continue
        country_code = "US"
        store_number = store["meta"]["id"]
        location_type = "<MISSING>"
        phone = store["mainPhone"]
        latitude = store["yextDisplayCoordinate"]["latitude"]
        longitude = store["yextDisplayCoordinate"]["longitude"]
        link = "https://fruttabowls.com/location/?location_id=" + store_number

        hours_of_operation = ""
        raw_hours = store["hours"]
        for day in raw_hours:
            try:
                opens = raw_hours[day]["openIntervals"][0]["start"]
                closes = raw_hours[day]["openIntervals"][0]["end"]
                clean_hours = day.title() + " " + opens + "-" + closes
            except:
                clean_hours = day.title() + " Closed"
            hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

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
