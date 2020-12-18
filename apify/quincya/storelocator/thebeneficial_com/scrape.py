import csv

from sgrequests import SgRequests


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []

    link = "https://www.wsfsbank.com/wsfs-api/GetLocatorSearchResults?AddressLine=&City=&State=&PostalCode=10010&Country=&Latitude=39.89457239999999&Longitude=-75.35845369999998&Type=FCS,&Offset=200"
    store_data = session.get(link, headers=headers).json()["locations"]["location"]

    locator_domain = "thebeneficial.com"

    for store in store_data:

        phone = "<MISSING>"
        location_type = "<MISSING>"

        attrs = store["attributes"]["attribute"]
        is_atm = False
        for attr in attrs:
            if attr["key"] == "LocationType":
                if attr["text"] == "ATM":
                    is_atm = True
                    break
            if attr["key"] == "LocationName":
                location_name = attr["text"]
            elif attr["key"] == "Phone":
                phone = attr["text"]

        if is_atm:
            continue

        page_url = "<MISSING>"

        store_number = store["id"]
        street_address = store["address"]["street"]
        city = store["address"]["city"]
        state = store["address"]["state"]
        zip_code = store["address"]["zip"]
        country_code = store["address"]["country"]
        hours_of_operation = " ".join(store["hours"]["hour"])
        latitude = store["address"]["lat"]
        longitude = store["address"]["long"]

        data.append(
            [
                locator_domain,
                page_url,
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
