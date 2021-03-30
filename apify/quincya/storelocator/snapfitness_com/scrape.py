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
        "Cookie": "PHPSESSID=e2cba0763a7db882913827a366d2ad57; _gcl_au=1.1.1726074005.1609905050; _ga=GA1.2.1727258516.1609905050; _gid=GA1.2.919295008.1609905050; _fbp=fb.1.1609905051574.1605161732; nmstat=1609905115034; _hjTLDTest=1; _hjid=a9fff4d2-9609-490d-a539-ec2f2014f1d5; _hjFirstSeen=1; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _hjIncludedInSessionSample=0; _gat_UA-1757587-27=1; PHPSESSID_2=6CSHS4VeqFdNnLcYzrsD96MszsJ3j1JkZkg%2F6Nytxz4u6uQLGPlx%2FREyIOKhxsDQzEvrbuZ1EISqNQPDH1j06Q%3D%3D",
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
        "lat": "40.3649407",
        "long": "-108.9700938",
        "radius": "4236.899793572078",
        "search": "",
    }

    res_json = session.post(base_link, headers=headers, data=payload).json()

    data = []
    for loc in res_json:

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
