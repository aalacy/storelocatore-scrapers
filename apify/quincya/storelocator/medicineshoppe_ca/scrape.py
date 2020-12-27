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

    base_link = "https://www.medicineshoppe.ca/api/sitecore/Pharmacy/Pharmacies?id=%7B4E561A90-2FD9-4AAC-ACCA-8572A82032AB%7D"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["pharmacies"]

    data = []
    locator_domain = "medicineshoppe.ca"

    for store in stores:
        location_name = store["title"]
        raw_address = store["address"].split(",")
        street_address = " ".join(raw_address[:-3])
        city = raw_address[-3].strip()
        state = raw_address[-2].replace("(", "").replace(")", "").strip()
        zip_code = raw_address[-1].strip()
        country_code = "CA"
        store_number = store["storeCode"]
        location_type = "<MISSING>"
        phone = store["phone"]
        latitude = store["location"]["latitude"]
        longitude = store["location"]["longitude"]
        link = "https://www.medicineshoppe.ca" + store["detailUrl"]

        hours_of_operation = ""
        raw_hours = store["storeOpeningHours"]
        for raw_hour in raw_hours:
            hours_of_operation = (
                hours_of_operation
                + " "
                + raw_hour["day"]
                + " "
                + raw_hour["openDuration"]
            ).strip()

        if store["temporarilyClosed"]:
            hours_of_operation = "Temporarily Closed"

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
