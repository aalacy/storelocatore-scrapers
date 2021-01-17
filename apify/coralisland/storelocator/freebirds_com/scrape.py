import csv

from sgrequests import SgRequests

base_url = "https://freebirds.com"


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    headers = {
        "authority": "cms.freebirds.chepri.com",
        "method": "GET",
        "path": "/fb/items/locations?fields=*.*&limit=-1",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "origin": "https://freebirds.com",
        "referer": "https://freebirds.com/locations",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-fetch-user": "?1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    output_list = []
    url = "https://cms.freebirds.chepri.com/fb/items/locations?fields=*.*&limit=-1"
    session = SgRequests()
    store_list = session.get(url, headers=headers).json()["data"]
    for store in store_list:
        output = []
        output.append(base_url)  # url
        output.append(store["name"])  # location name
        output.append(store["address_1"])  # address
        output.append(store["city"])  # city
        output.append(store["state"])  # state
        output.append(store["zip_code"])  # zipcode
        output.append("US")  # country code
        output.append(store["olo_store_id"])  # store_number
        output.append(store["phone_number"])  # phone
        output.append("<MISSING>")  # location type
        output.append("<MISSING>")  # latitude
        output.append("<MISSING>")  # longitude
        output.append("<INACCESSIBLE>")  # opening hours
        output.append(store["rio_url"])  # page url
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
