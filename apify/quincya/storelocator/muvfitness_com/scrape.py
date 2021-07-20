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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.muvfitness.com/locations/?CallAjax=GetLocations"

    session = SgRequests()
    stores = session.post(base_link, headers=headers).json()

    data = []
    locator_domain = "https://www.muvfitness.com/"

    for store in stores:
        location_name = store["FranchiseLocationName"]
        street_address = (store["Address1"] + " " + store["Address2"]).strip()
        city = store["City"]
        state = store["State"]
        zip_code = store["ZipCode"]
        country_code = "US"
        store_number = store["FranchiseLocationID"]
        location_type = "<MISSING>"
        phone = store["Phone"]
        latitude = store["Latitude"]
        longitude = store["Longitude"]
        link = "https://www.muvfitness.com" + store["Path"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        hours_of_operation = (
            " ".join(list(base.find(class_="gym-hours").stripped_strings))
            .split("Hours")[1]
            .strip()
        )
        if "mon" not in hours_of_operation.lower():
            hours_of_operation = "<MISSING>"
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
