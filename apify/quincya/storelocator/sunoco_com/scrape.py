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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.sunoco.com/js/locations.json"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    data = []
    found = []
    locator_domain = "sunoco.com"

    for store in stores:
        location_name = "SUNOCO #" + str(store["Store_ID"])
        if location_name in found:
            continue
        found.append(location_name)
        street_address = store["Street_Address"].replace("  ", " ")
        city = store["City"]
        if "24205" in city:
            street_address = city
            city = "Farmington Hills".upper()
        state = store["State"]
        zip_code = str(store["Postalcode"])
        if len(zip_code) < 5:
            zip_code = "0" + zip_code
        if len(zip_code) < 4:
            zip_code = "<MISSING>"
        country_code = "US"
        store_number = store["Store_ID"]
        location_type = "<MISSING>"
        phone = store["Phone"]
        if len(str(phone)) < 5:
            phone = "<MISSING>"
        hours_of_operation = (
            "Mon %s Tue %s Wed %s Thu %s Fri %s Sat %s Sun %s"
            % (
                store["MON_Hours"],
                store["TUE_Hours"],
                store["WED_Hours"],
                store["THU_Hours"],
                store["FRI_Hours"],
                store["SAT_Hours"],
                store["SUN_Hours"],
            )
        ).strip()

        latitude = store["Latitude"]
        longitude = store["Longitude"]
        if not latitude or latitude == "NULL":
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        link = "<MISSING>"

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
