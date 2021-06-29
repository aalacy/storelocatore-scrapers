import csv

from sgrequests import SgRequests


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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    session = SgRequests()

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "65",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.snapfitness.com",
        "Origin": "https://www.snapfitness.com",
        "Referer": "https://www.snapfitness.com/us/gyms/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    locator_domain = "snapfitness.com"

    base_link = "https://www.snapfitness.com/us/gyms/relevantLocations"

    payload = {
        "lat": "44.977753",
        "limitToCountry": "true",
        "long": "-93.265015",
        "radius": "4236.899793572078",
        "search": "",
    }

    res_json = session.post(base_link, headers=headers, data=payload).json()

    data = []
    for i in res_json:
        loc = res_json[i]
        location_name = "Snap Fitness " + loc["Name"].strip()

        phone_number = loc["PhoneNumber"]
        if not phone_number:
            phone_number = "<MISSING>"
        lat = loc["Latitude"]
        longit = loc["Longitude"]
        try:
            street_address = (loc["Address1"] + " " + loc["Address2"]).strip()
        except:
            street_address = loc["Address1"]
        city = loc["City"]
        state = loc["State"]
        zip_code = loc["Postcode"]
        country_code = loc["Country"]
        if "US" in country_code:
            country_code = "US"
        elif "CA" in country_code:
            country_code = "CA"
        else:
            continue
        store_number = loc["ID"]

        hours = "<INACCESSIBLE>"
        page_url = "https://www.snapfitness.com/" + loc["URL"]
        location_type = "<MISSING>"

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

        data.append(store_data)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
