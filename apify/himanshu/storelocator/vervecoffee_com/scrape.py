import csv
from sgrequests import SgRequests
from datetime import datetime

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
    addressess = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    link_list = [
        "https://instore.vervecoffee.com/app/store/api/v13/editor/users/131224020/sites/910488912954480986/store-locations?page=1&per_page=100&include=address&lang=en",
        "https://instore.vervecoffee.com/app/store/api/v13/editor/users/131224020/sites/910488912954480986/store-locations?page=1&per_page=100&include=address&lang=en&fulfillment_methods[]=pickup",
    ]

    for link in link_list:
        json_data = session.get(link, headers=headers).json()
        for value in json_data["data"]:
            location_name = value["address"]["data"]["business_name"]
            if value["address"]["data"]["street2"]:
                street_address = (
                    value["address"]["data"]["street"]
                    + " "
                    + value["address"]["data"]["street2"]
                )
            else:
                street_address = value["address"]["data"]["street"]
            city = value["address"]["data"]["city"]
            state = value["address"]["data"]["region_code_full_name"]
            zip = value["address"]["data"]["postal_code"]
            country_code = value["address"]["data"]["country_code"]
            if value["address"]["data"]["phone"] is not None:
                phone = value["address"]["data"]["phone"]
            else:
                phone = "<MISSING>"

            if value["address"]["data"]["latitude"] is not None:
                latitude = value["address"]["data"]["latitude"]
                longitude = value["address"]["data"]["longitude"]
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            page_url = "https://instore.vervecoffee.com/?location=" + value["id"]
            hours_of_operation = (
                "Every day / "
                + datetime.strptime(
                    value["pickup_hours"]["MON"][0]["open"], "%H:%M:%S"
                ).strftime("%I:%M %p")
                + " - "
                + datetime.strptime(
                    value["pickup_hours"]["MON"][0]["close"], "%H:%M:%S"
                ).strftime("%I:%M %p")
            )
            page_url = "https://instore.vervecoffee.com/?location=" + value["id"]

            if (
                page_url
                == "https://instore.vervecoffee.com/?location=11ea6569302c7257a76c0cc47a2b1e8c"
            ):
                continue
            store = []
            store.append("https://www.vervecoffee.com/")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[-1] in addressess:
                continue
            addressess.append(store[-1])
            store = [
                str(x).replace("–", "-").strip() if x else "<MISSING>" for x in store
            ]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
