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
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }

    base_url = "https://www.thetamalekitchen.com"
    r = session.get("https://www.thetamalekitchen.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for script in soup.find(id="SITE_PAGES").find_all(
        "div", {"data-testid": "richTextElement"}
    ):
        list_store_data = list(script.stripped_strings)

        street_address = list_store_data[0].split(",")[0]

        hours_of_operation = "<MISSING>"
        phone = "<MISSING>"

        for element in list_store_data:
            if "(" in element:
                phone = element.split(" (")[0]

            elif "-" in element and "pm" in element:
                if "<MISSING>" in hours_of_operation:
                    hours_of_operation = ",".join(
                        list_store_data[list_store_data.index(element) :]
                    )
                    if "(" in hours_of_operation:
                        hours_of_operation = hours_of_operation[
                            : hours_of_operation.find(",(")
                        ]

        country_code = "US"

        if len(list_store_data[0].split(",")) == 2:
            state = list_store_data[0].split(",")[1].strip().split(" ")[0]
            zipp = list_store_data[0].split(",")[1].strip().split(" ")[1]
            city = "<MISSING>"
        elif len(list_store_data[0].split(",")) == 3:
            state = list_store_data[0].split(",")[2].strip().split(" ")[0]
            zipp = list_store_data[0].split(",")[2].strip().split(" ")[1]
            city = list_store_data[0].split(",")[1]
        else:
            city = list_store_data[1].split(",")[0]
            state = list_store_data[1].split(",")[1].strip().split(" ")[0]
            zipp = list_store_data[1].split(",")[1].strip().split(" ")[1]

        if "Lakewood" in street_address:
            street_address = street_address.replace("Lakewood", "").strip()
            city = "Lakewood"

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_name = "TAMALE KITCHEN " + city.strip()

        store = [
            locator_domain,
            location_name,
            street_address,
            city.strip(),
            state,
            zipp,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
            "https://www.thetamalekitchen.com/locations",
        ]
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
