import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

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


def fetch_data():
    return_main_object = []

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "accept": "application/json, text/javascript, */*; q=0.01",
    }

    # it will used in store data.
    base_url = "https://lotsa.com"
    locator_domain = "https://lotsa.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    r = session.get("https://lotsa.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for a in soup.find_all("a", class_="et_pb_custom_button_icon"):
        page_url = base_url + a["href"]
        r_loc = session.get(base_url + a["href"], headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, "lxml")

        div = soup_loc.find("div", class_="et_pb_row et_pb_row_12").find(
            class_="et_pb_text_inner"
        )

        list_div = list(div.stripped_strings)
        phone = list_div[0]
        street_address = list_div[1]
        city = list_div[2].split(",")[0]
        state = list_div[2].split(",")[-1].split()[0]
        zipp = list_div[2].split(",")[-1].split()[-1]
        location_name = city + ", " + state
        hours_of_operation = " ".join(list_div[5:]).split("Outside")[0].strip()

        latitude = soup_loc.find(class_="et_pb_map")["data-center-lat"]
        longitude = soup_loc.find(class_="et_pb_map")["data-center-lng"]
        store = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zipp,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
            page_url,
        ]
        store = ["<MISSING>" if x == "" else x for x in store]
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
