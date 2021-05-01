import csv
from sgrequests import SgRequests
from sgselenium import SgSelenium
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    driver = SgSelenium().chrome()
    addresses = []
    base_url = "https://www.midfirst.com"
    driver.get("https://www.midfirst.com/locations")
    cookies_list = driver.get_cookies()
    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie["name"]] = cookie["value"]
    cookies_string = (
        str(cookies_json)
        .replace("{", "")
        .replace("}", "")
        .replace("'", "")
        .replace(": ", "=")
        .replace(",", ";")
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "cookie": cookies_string,
        "accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    r_token = session.get("https://www.midfirst.com/api/Token/get", headers=headers)
    token_for_post = r_token.json()["Token"]
    token_for_cookie = r_token.headers["Set-Cookie"].split(";")[0] + ";"

    cookies_string = (
        str(cookies_json)
        .replace("{", "")
        .replace("}", "")
        .replace("'", "")
        .replace(": ", "=")
        .replace(",", ";")
    )

    final_cookies_string = cookies_string + ";" + token_for_cookie

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "cookie": final_cookies_string,
        "accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
    }

    addresses = []
    mylist = static_coordinate_list(100, SearchableCountries.USA)
    MAX_RESULTS = 25
    MAX_DISTANCE = 150
    p = 0

    base_url = "https://www.midfirst.com"
    data = []
    for lat, lng in mylist:
        try:
            json_data = session.post(
                "https://www.midfirst.com/api/Locations",
                headers=headers,
                data="location-banking-center=on&location-atm=on&location-distance="
                + str(MAX_DISTANCE)
                + "&location-count="
                + str(MAX_RESULTS)
                + "&location-lat="
                + str(lat)
                + "&location-long="
                + str(lng)
                + "&__RequestVerificationToken="
                + token_for_post,
            ).json()["FilteredResults"]

            check = len(json_data)
            if check > 0:
                pass
        except:
            continue
        for location in json_data:
            store_number = str(location["Ref"])
            location_name = location["Name"]
            phone = location["PhoneNumber"]
            latitude = str(location["Latitude"])
            longitude = str(location["Longitude"])
            street_address = location["Address1"] + " " + location["Address2"]
            zipp = location["PostalCode"]
            location_type = location["LocationType"]["Name"]
            city = location["City"]["Name"]
            state = location["State"]["Name"]
            link = base_url + location["DetailsPath"]
            hours_of_operation = ""
            for day_hours in location["Schedules"]:
                close = (int)(day_hours["ClosingTime"].split(":")[0])
                if close > 12:
                    close = close - 12
                hours_of_operation += (
                    day_hours["DayOfWeek"]["Name"]
                    + " "
                    + day_hours["OpeningTime"].split(":")[0]
                    + ":"
                    + day_hours["OpeningTime"].split(":")[1]
                    + " AM - "
                    + str(close)
                    + ":"
                    + day_hours["ClosingTime"].split(":")[1]
                    + " PM "
                )
            if street_address in addresses:
                continue
            if (len(phone)) < 3:
                phone = "<MISSING>"
            if len(hours_of_operation) < 3:
                hours_of_operation = "<MISSING>"
            addresses.append(street_address)
            data.append(
                [
                    base_url,
                    link,
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    "US",
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )

            p += 1
    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
