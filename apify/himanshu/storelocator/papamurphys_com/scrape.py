import csv
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    base_url = "https://www.papamurphys.com/"
    headers = {
        "content-type": "application/json; charset=UTF-8",
        "x-olo-request": "1",
        "accept": "*/*",
    }
    state_url = "https://order.papamurphys.com/api/vendors/regions?excludeCities=true"

    state_json = session.get(state_url, headers=headers).json()

    for st in state_json:
        url = "https://order.papamurphys.com/api/vendors/search/" + st["code"]
        json_data = session.get(url, headers=headers).json()
        for val in json_data["vendor-search-results"]:
            location_name = val["name"]
            street_address = val["address"]["streetAddress"]
            city = val["address"]["city"]
            state = val["address"]["state"]
            zipp = val["address"]["postalCode"]
            country_code = val["address"]["country"]
            store_number = val["id"]
            temp_phone = val["phoneNumber"].lstrip("1")
            phone = "(" + temp_phone[:3] + ") " + temp_phone[3:6] + "-" + temp_phone[6:]
            latitude = val["latitude"]
            longitude = val["longitude"]
            page_url = "https://order.papamurphys.com/menu/" + val["slug"]
            hours = val["weeklySchedule"]["calendars"][0]["schedule"]
            hours_of_operation = []
            for h in hours:
                frame = h["weekDay"] + " " + h["description"]
                hours_of_operation.append(frame)
            hours_of_operation = ", ".join(hours_of_operation)

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append("Papa Murphy")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
