import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()


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


def fetch_data():
    return_main_object = []
    addresses = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    base_url = "https://www.thefreshgrocer.com"

    zip_code = "08311"
    r = session.post(
        "https://shop.thefreshgrocer.com/StoreLocatorSearch",
        headers=headers,
        data="Region=&SearchTerm="
        + str(zip_code)
        + "&Radius=10000&Take=9999&Redirect=",
    )
    soup = BeautifulSoup(r.text, "lxml")

    locator_domain = base_url
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

    for script in soup.find_all("li", {"class": "stores__store"}):
        list_address = list(
            script.find("div", {"class": "store__address"}).stripped_strings
        )
        list_hours = []
        for hour in script.find_all(
            "p", {"class": "hoursAndServices__schedule storeDetails__content"}
        ):
            list_hours.append(list(hour.stripped_strings))

        if list_address[0] in addresses:
            continue

        addresses.append(list_address[0])

        map_url = script.find("div", {"class": "store__controls"}).find("a")["href"]
        street_address = list_address[0]
        phone = list_address[-1]
        city = list_address[1].split(",")[0]
        state = list_address[1].split(",")[-1].strip().rsplit(" ", 1)[0]
        zipp = list_address[1].split(",")[-1].strip().rsplit(" ", 1)[-1]
        hours_of_operation = ""
        final_hours_list = []
        for hour in list_hours:
            final_hours_list.append("".join(hour).replace("–", "-").strip())

        hours_of_operation = "; ".join(final_hours_list)
        location_name = city
        latitude = map_url.split("?daddr=")[1].split(",")[0]
        longitude = map_url.split("?daddr=")[1].split(",")[1]

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

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
