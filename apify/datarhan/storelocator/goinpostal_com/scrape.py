import csv
import json

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
    # Your scraper here
    session = SgRequests()

    items = []

    DOMAIN = "goinpostal.com"

    start_url = (
        "https://goinpostal.com/wp-admin/admin-ajax.php?action=get_stores_by_zipcode"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    formdata = {"zipcode": "10001", "distance": "50000"}

    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = (
            "https://goinpostal.com/locations/locator_store.php/?storeID={}".format(
                poi["store_id_old"]
            )
        )
        location_name = poi["store_name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["store_address"]
        location_type = "<MISSING>"
        if "Coming Soon" in street_address:
            location_type = "Coming Soon"
        street_address = (
            street_address.replace("Coming Soon", "") if street_address else "<MISSING>"
        )
        street_address = street_address if street_address.strip() else "<MISSING>"
        city = poi["store_city"]
        city = city if city else "<MISSING>"
        state = poi["store_state"]
        state = state.replace(".", "") if state else "<MISSING>"
        zip_code = poi["store_zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["store_id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["store_phone"]
        if "Coming Soon" in phone:
            phone = "<MISSING>"
        phone = phone if phone else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"

        mon = "Monday {}".format(poi["hour_work_Mon"])
        tue = "Tuesday {}".format(poi["hour_work_Tue"])
        wen = "Wednesday {}".format(poi["hour_work_Wed"])
        thu = "Thursday {}".format(poi["hour_work_Thu"])
        fri = "Friday {}".format(poi["hour_work_Fri"])
        sat = "Saturday {}".format(poi["hour_work_Sat"])
        sun = "Sunday {}".format(poi["hour_work_Sun"])
        hours_of_operation = [mon, tue, wen, thu, fri, sat, sun]
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        if "soon" in hours_of_operation.lower():
            location_type = "Coming Soon"
        if poi["coding"] == "N":
            location_type = "Coming Soon"

        item = [
            DOMAIN,
            store_url,
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
