import csv
from sgselenium import SgChrome


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def addy_ext(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():
    locator_domain = "http://www.empireeatery.com/"
    ext = "find-us-.html"

    with SgChrome() as driver:
        driver.get(locator_domain + ext)

        cont = driver.find_element_by_css_selector("div.txt ").text.split("\n")

        all_store_data = []
        spin = 0

        clean_cont = []
        for c in cont:
            if c == "":
                continue
            clean_cont.append(c)

        for c in clean_cont:
            if spin == 0:
                street_address = c
            elif spin == 1:
                city, state, zip_code = addy_ext(c)
            elif spin == 2:
                phone_number = c

                if "PORT BYRON" in city:
                    hours = "Mon-Sat 5am-11pm Sunday 6am-11pm"
                elif "WEEDSPORT" in city:
                    hours = "24 hours"
                elif "GENOA" in city:
                    hours = "MON-THURS 5AM-10PM FRI- SAT 5AM-11PM SUN 6AM-10PM"
                elif "FULTON" in city:
                    hours = "MON-SAT 5 AM- 11PM SUNDAY 6AM-10PM"
                else:
                    hours = "<MISSING>"

                country_code = "US"

                location_type = "<MISSING>"
                page_url = "http://www.empireeatery.com/find-us-.html"
                longit = "<MISSING>"
                lat = "<MISSING>"
                store_number = "<MISSING>"
                location_name = city

                store_data = [
                    locator_domain,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country_code,
                    store_number,
                    phone_number,
                    location_type,
                    lat,
                    longit,
                    hours,
                    page_url,
                ]
                all_store_data.append(store_data)

                spin = -1
            spin += 1

        driver.quit()
        return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
