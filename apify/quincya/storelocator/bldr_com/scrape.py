import csv

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

    base_link = "https://bldr-back-central.azurewebsites.net//umbraco/api/LocationData/GetAllLocations"

    session = SgRequests()

    json = {"radius": 150, "DistributionList": "", "installedServiceName": ""}

    stores = session.post(base_link, headers=headers, json=json).json()

    data = []
    locator_domain = "bldr.com"

    for store in stores:
        location_name = store["Name"]
        street_address = (store["Address1"] + " " + store["Address2"]).strip()
        city = store["City"]
        state = store["State"]
        zip_code = store["ZipCode"]
        country_code = "US"
        store_number = store["Id"]
        location_type = "<MISSING>"
        phone = store["PhoneNo"].replace("Call to make an appointment", "").strip()
        try:
            mon_fri = "Mon-Fri " + store["HoursMFNew"]
        except:
            mon_fri = ""
        try:
            sat = " Sat " + store["HoursSat"]
        except:
            sat = ""
        try:
            sun = " Sun " + store["HoursSun"]
        except:
            sun = ""
        hours_of_operation = (
            (mon_fri + sat + sun).replace(",", "-").replace("0-0", "Closed").strip()
        )

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        latitude = store["Latitude"]
        longitude = store["Longitude"]
        link = "https://bldr.com" + store["Url"]

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
