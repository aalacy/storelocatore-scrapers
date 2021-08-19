import csv

from sgrequests import SgRequests

session = SgRequests()


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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    r = session.get(
        "https://api.riddlesjewelry.com/storelocator/index/loadstore/?radius=10000&latitude=38.8619254&longitude=-97.654811&type=all",
        headers=headers,
    )

    store_name = []
    store_detail = []
    return_main_object = []
    k = r.json()
    for idx, val in enumerate(k["storesjson"]):
        tem_var = []
        street_address1 = val["address"]
        phone = val["phone"]
        latitude = val["latitude"]
        longitude = val["longitude"]
        zipcode = val["zipcode"]
        state = val["state"]
        city = val["city"]
        data_new = " IN " + str(city.upper()) + "," + str(state.upper())
        store_name.append(val["store_name"].upper() + str(data_new))
        tem_var.append(street_address1.replace(", Pueblo, CO 81008, USA", ""))
        tem_var.append(city if city else "<MISSING>")
        tem_var.append(state if state else "<MISSING>")
        tem_var.append(zipcode if zipcode else "<MISSING>")
        tem_var.append("US")
        tem_var.append(val["storelocator_id"])
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        page_url = (
            "https://www.riddlesjewelry.com/storelocator/index/details?locatorId="
            + val["storelocator_id"]
        )

        hours_of_operation = ""
        days = [
            "monday_",
            "tuesday_",
            "wednesday_",
            "thursday_",
            "friday_",
            "saturday_",
            "sunday_",
        ]
        for day in days:
            if val[day + "status"] == "1":
                hours = val[day + "open"] + "-" + val[day + "close"]
            else:
                hours = "Closed"
            hours_of_operation = (
                hours_of_operation + " " + day.title().replace("_", "") + " " + hours
            ).strip()

        tem_var.append(hours_of_operation)
        tem_var.append(page_url)
        store_detail.append(tem_var)
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.riddlesjewelry.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
