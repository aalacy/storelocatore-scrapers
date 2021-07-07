import csv
import re

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    session = SgRequests()

    found = []
    base_url = "https://www.orangetheory.com"
    for country_url in [
        "https://www.orangetheory.com/bin/otf/getStudioPagesDetail.en_ca.json",
        "https://www.orangetheory.com/bin/otf/getStudioPagesDetail.en_us.json",
    ]:
        json_data = session.get(country_url).json()["data"]

        i = 1
        for data in json_data:
            if "https" in data["studioURL"]:
                page_url = data["studioURL"]
            else:
                page_url = base_url + data["studioURL"]

            # New session every 50
            if i % 50 == 0:
                session = SgRequests()

            i += 1

            store_number = data["studioID"]
            if store_number in found:
                continue
            found.append(store_number)

            location_data = session.get(
                "https://api.orangetheory.co/partners/studios/v2?latitude=&longitude=&distance=&country=&studioId="
                + str(store_number)
            ).json()
            try:
                for loc in location_data["data"][0]:
                    location_name = loc["studioName"]
                    loc_type = loc["studioStatus"]
                    if "coming soon" in loc_type.lower():
                        continue
                    street_address = re.sub(
                        r"\s+",
                        " ",
                        loc["studioLocation"]["physicalAddress"].split(
                            "Street, New York"
                        )[0],
                    ).strip()
                    city = loc["studioLocation"]["physicalCity"]
                    state = loc["studioLocation"]["physicalState"]
                    zipp = loc["studioLocation"]["physicalPostalCode"]
                    if "9201 Winnetka Ave" in street_address:
                        zipp = "91311"
                    country_code = (
                        loc["studioLocation"]["physicalCountry"]
                        .replace("Canada", "CA")
                        .replace("United States", "US")
                    )
                    if loc["studioLocation"]["phoneNumber"]:
                        phone = loc["studioLocation"]["phoneNumber"].replace(".", "")
                    else:
                        phone = "<MISSING>"
                    latitude = loc["studioLocation"]["latitude"]
                    longitude = loc["studioLocation"]["longitude"]
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append(country_code)
                    store.append(store_number)
                    store.append(phone)
                    store.append(loc_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append("<MISSING>")
                    store.append(page_url)
                    store = [str(x).strip() if x else "MISSING" for x in store]
                    yield store
            except:
                pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
