import csv
from sgrequests import SgRequests


def fetch_data():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    # data = 'ajax=1&action=get_nearby_stores&distance=100000&suzukitype=matv&storetype=undefined&lat=43.7086666&lng=-79.30808809999996'
    base_url = "https://www.suzuki.ca"
    r = session.get(
        "https://www.suzuki.ca/wp-json/wpgmza/v1/markers/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUgsSKgYLRsbVKtQCV7hBN",
        headers=headers,
    )
    location_data = r.json()
    for i in location_data:
        latitude = i["lat"]
        longitude = i["lng"]
        location_name = i["title"]
        link = i["link"]
        if link == "" or link == "\xa0":
            link = "<MISSING>"
        j = i["custom_field_data"]
        phone = ""
        state = ""
        zipp = ""
        city = ""
        store_number = ""
        street_address = ""
        for k in j:
            if k["id"] == 1:
                phone = k["value"]
            if k["id"] == 3:
                store_number = k["value"]
            if k["id"] == 4:
                street_address = k["value"]
            if k["id"] == 5:
                city = k["value"]
            if k["id"] == 6:
                state = k["value"]
            if k["id"] == 7:
                zipp = k["value"]
            if k["id"] == 8:
                type = k["value"]
        store = []
        store.append(base_url)
        store.append(link)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("CA")
        store.append(store_number)
        store.append(phone)
        store.append(type)
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        yield store


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
