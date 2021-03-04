import csv
from sgselenium import SgSelenium
import json


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    locator_domain = "https://www.mixt.com/"
    ext = "locations/"

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    stores = driver.find_elements_by_css_selector("div.grand-text")

    all_store_data = []
    ignored = []
    for store in stores:
        content = store.text.split("\n")
        if "OPENING SOON" in content[0]:
            ignored.append(content)
            continue
        if "Delivery Only" in content:
            ignored.append(content)
            continue
        if len(content) > 3:
            if "CITY CENTER BISHOP RANCH" in content[0]:
                street_address = content[1]
                city, state, zip_code = addy_ext(content[2])
            else:
                if "Los Angeles" in content[2]:
                    street_address = content[1]
                else:
                    street_address = content[0]
                city, state, zip_code = addy_ext(content[2])

            hours = ""
            for h in content[3:-2]:
                hours += h + " "

            country_code = "US"
            location_type = "<MISSING>"
            phone_number = "<MISSING>"
            lat = ""
            lon = ""
            location_name = ""
            store_number = ""

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
                lon,
                hours,
            ]
            all_store_data.append(store_data)
    script = driver.find_element_by_xpath("/html/body/script[1]").get_attribute(
        "innerHTML"
    )
    script = json.loads(
        str('[{"id"' + script.split('{"id"', 1)[1].rsplit('"}', 1)[0] + '"}]')
    )
    topop = []
    for i, val in enumerate(script):
        for j in ignored:
            if val["title"] in j:
                topop.append(i)
    for i in reversed(topop):
        script.pop(i)
    driver.quit()
    for i, val in enumerate(all_store_data):
        all_store_data[i][1] = script[i]["title"]
        all_store_data[i][-3] = script[i]["lat"]
        all_store_data[i][-2] = script[i]["lng"]
        all_store_data[i][7] = script[i]["id"]

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
