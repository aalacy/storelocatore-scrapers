import csv
from sgrequests import SgRequests
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("smoothieking_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
    addresses = []
    base_url = "https://smoothieking.com"
    for page in range(1, 54):
        json_r = session.get(
            "https://momentfeed-prod.apigee.net/api/llp.json?auth_token=TLLLFMCOPXOWXFMY&center=38.541749,-98.428791&multi_account=false&page="
            + str(page)
        ).json()
        for data in json_r:
            if data["store_info"]["status"] == "coming soon":
                continue
            street_address = data["store_info"]["address"]
            if data["store_info"]["address_extended"]:
                street_address = (
                    street_address + " " + data["store_info"]["address_extended"]
                )
            city = data["store_info"]["locality"]
            state = data["store_info"]["region"]
            zipp = data["store_info"]["postcode"]
            country_code = data["store_info"]["country"]
            phone = data["store_info"]["phone"]
            latitude = data["store_info"]["latitude"]
            longitude = data["store_info"]["longitude"]
            location_name = data["store_info"]["name"]
            page_url = data["store_info"]["website"]
            if page_url == "https://www.smoothieking.com/":
                page_url = (
                    "https://locations.smoothieking.com/ll/US/"
                    + str(state)
                    + "/"
                    + str(city)
                    + "/"
                    + str(
                        street_address.replace(" ", "-")
                        .replace(".", "_")
                        .replace(",", "*")
                    )
                )
            store_number = data["store_info"]["corporate_id"]
            location_type = data["store_info"]["brand_name"]

            if data["store_info"]["store_hours"]:
                hours = data["store_info"]["store_hours"].split(";")
                del hours[-1]
                date = ""
                day = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                for time in range(len(hours)):
                    start_time = datetime.strptime(
                        str(hours[time].split(",")[1]), "%H%M"
                    ).strftime("%I:%M %p")
                    end_time = datetime.strptime(
                        str(hours[time].split(",")[2]), "%H%M"
                    ).strftime("%I:%M %p")
                    try:
                        date += (
                            day[time]
                            + " "
                            + str(start_time)
                            + "-"
                            + str(end_time)
                            + " "
                        )
                    except:
                        date = "<MISSING>"
                if len(hours) == 5:
                    hours_of_operation = date + "Saturday Closed Sunday Closed"
                else:
                    hours_of_operation = date
            else:
                hours_of_operation = "<MISSING>"

            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
