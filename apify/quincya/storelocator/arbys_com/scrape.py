import csv

from bs4 import BeautifulSoup

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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://api.arbys.com/web-exp-api/v1/location?latitude=31.9685988&longitude=-99.9018131&radius=10000&limit=5000&page=1"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    data = []
    locator_domain = "arbys.com"

    for store in stores:
        location_name = store["displayName"]
        raw_address = store["contactDetails"]["address"]
        street_address = (
            (
                raw_address["line1"]
                + " "
                + raw_address["line2"].title()
                + " "
                + raw_address["line3"].title()
            )
            .replace("Building H 4512", "")
            .strip()
        )
        city = raw_address["city"]
        state = raw_address["stateProvinceCode"]
        zip_code = raw_address["postalCode"]
        if "1299 Oxford Street" in street_address:
            zip_code = "N5Y 4W5"
        if "26361 Fraser Hwy" in street_address:
            zip_code = "V4W 2Z7"
        country_code = raw_address["countryCode"]
        if country_code not in ["US", "CA"]:
            continue
        store_number = store["storeId"]
        try:
            location_type = store["status"]
        except:
            location_type = "<MISSING>"
        hours = store["hours"]
        hours_of_operation = ""
        for h in hours:
            day = h["dayOfWeek"]
            open_time = h["openTime"]
            close_time = h["closeTime"]
            if open_time:
                clean_hours = open_time + "-" + close_time
            else:
                clean_hours = "Closed"
            hours_of_operation = (
                hours_of_operation + " " + day + " " + clean_hours
            ).strip()
        if not hours_of_operation:
            continue
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "<MISSING>"
        latitude = store["details"]["latitude"]
        longitude = store["details"]["longitude"]
        if str(latitude) == "-1":
            continue
        link = (
            "https://locations.arbys.com/"
            + state.lower()
            + "/"
            + city.lower()
            .replace(" ", "")
            .replace(".", "-")
            .replace("lewismcchord", "lewis-mcchord")
            + "/"
            + raw_address["line1"].strip().lower().replace(" ", "-").replace(",", "")
            + ".html"
        )

        if "store-#31a" in link and location_type == "<MISSING>":
            continue

        location_type = "<MISSING>"
        phone = store["contactDetails"]["phone"]
        if not phone:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            phone = base.find(class_="phone ga-link").text

        if not location_name:
            location_name = "Arby's – " + city

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
