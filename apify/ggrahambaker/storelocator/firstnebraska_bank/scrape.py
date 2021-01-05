import csv
from sgselenium import SgSelenium


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


def addy_ext(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def phone_cut(arr):
    for i, a in enumerate(arr):
        if "Phone" in a:
            return i


def fetch_data():
    locator_domain = "https://www.firstnebraska.bank/"
    ext = "locations/"

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    divs = driver.find_elements_by_css_selector("div.location")
    all_store_data = []
    for div in divs:
        content = div.text.split("\n")
        if "coming soon" in div.text.lower():
            continue
        location_name = content[0]

        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])

        phone_idx = phone_cut(content)

        hours = ""

        for h in content[3:phone_idx]:
            hours += h + " "

        phone_number = content[phone_idx].replace("Phone:", "").strip()

        lat = "<MISSING>"
        longit = "<MISSING>"

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        country_code = "US"

        store_data = [
            locator_domain,
            "https://www.firstnebraska.bank/locations/",
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
        ]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
