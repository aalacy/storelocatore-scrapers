import csv
import json
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
    base_url = "https://www.furniturerow.com/"
    payload = {
        "filter": {
            "postalCode": "75074",
            "country": "USA",
            "term": {
                "cond": {
                    "property": "locationType",
                    "comparator": "eq",
                    "value": "storeCluster",
                }
            },
        },
        "page": 0,
        "pageSize": 1000,
        "orders": [],
    }
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "cookie": "__cfduid=df89cff2a759ef81568185d07af6206191610530766; guestToken=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3Vwc3RhcnRjb21tZXJjZS5jb20iLCJzdWIiOiJkZW52ZXJtYXR0cmVzczpjdXN0b21lcjozZTU2NGEyMC03ZmQxLTRjODAtYTBmZi1lNjJjMmExNDQwNTMiLCJpYXQiOjE2MTA1MzA3NjgsInVzZXJJZCI6IjNlNTY0YTIwLTdmZDEtNGM4MC1hMGZmLWU2MmMyYTE0NDA1MyIsImxvZ2luIjoiYW5vbnltb3VzIiwidGVuYW50TWFwIjp7ImRlbnZlcm1hdHRyZXNzIjp7InJvbGVzIjpbImN1c3RvbWVyLmFub255bW91cyJdLCJwZXJtaXNzaW9ucyI6W10sInNpdGVzIjp7IjIwMWNiNzg5LTQxOTgtNDg4Yi1hNWViLTRlN2RmMGZiNGJlZSI6eyJyb2xlcyI6W10sInBlcm1pc3Npb25zIjpbXX0sIjhkM2VhM2JjLWY2NWItNDIyNy05ZmE2LTZmYWU0MGU0NTc1YSI6eyJyb2xlcyI6W10sInBlcm1pc3Npb25zIjpbXX19fX0sInRva2VuVHlwZSI6IkFjY2VzcyIsInRlbmFudCI6ImRlbnZlcm1hdHRyZXNzIiwiZG9tYWluIjoiY3VzdG9tZXIiLCJzdWJqZWN0VHlwZSI6IkFub255bW91cyIsImlzQW5vbnltb3VzIjp0cnVlLCJ0cGUiOiJBQ0NFU1MifQ._yhKMPGi5Vy0Nr-b0xneT5X04QLqmyyWkzwC3ZLZkbk; location=%7B%22postalCode%22%3A%2275074%22%2C%22latitude%22%3A%2233.03%22%2C%22longitude%22%3A%22-96.68%22%7D; store=%7B%22id%22%3A%22100068%22%2C%22name%22%3A%22TX-Sherman-Furniture%20Row%20Shopping%20Center%22%2C%22address%22%3A%7B%22street1%22%3A%222201%20Hwy%2075%20North%22%2C%22street2%22%3A%22%22%2C%22city%22%3A%22Sherman%22%2C%22stateOrRegion%22%3A%22TX%22%2C%22country%22%3A%22US%22%2C%22postalCode%22%3A%2275090%22%7D%2C%22coordinates%22%3A%7B%22latitude%22%3A33.658727%2C%22longitude%22%3A-96.610655%7D%2C%22locationType%22%3A%22Furniture%20Row%C2%AE%22%2C%22storeId%22%3A%22700280%22%2C%22pricingZone%22%3A%22SHERMAN%22%2C%22e%22%3A1610617168588%7D; subscribePopup=false; _gcl_au=1.1.1017281312.1610530778; _ga=GA1.2.1771174579.1610530784; _gid=GA1.2.1283454543.1610530784; btpdb.YOoTwyE.dGZjLjU0ODM4MzU=U0VTU0lPTg; _fbp=fb.1.1610530804381.1201758717; dtm_token=AQEDIUrgNnAbMwELWxKvAQHwIwE; _uetsid=4322d9f0558311eba81a5f5beedf537b; _uetvid=4322ee70558311ebb5195f9813da1d19; _gat_UA-31665-1=1; xdibx=N4Ig-mBGAeDGCuAnRIBcoAOGAuBnNAjAGwEAMArAMwBMlAHACwCcTA7ADQgYBusAdtjSVOufKmJkqpVk1IF5nHrn6DUwkIiQAbNCBCct23QHotAe1gBDbAEszffAbyESFStNnyCAX04QYGIgAptxooAAmlgCeYgDaEm4ecgQMALq-4FDQIUECYsAZ.nA24brhkJZBQQxWALSw4eHktQzkrES1kKTUHbCQrHQEdExkAGaQlLUJUgOsDATkIN5AA__",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "x-upstart-tenant": "denvermattress",
    }
    res = session.post(
        "https://www.furniturerow.com/v1/location/search/postalcode",
        json=payload,
        headers=headers,
    )
    store_list = json.loads(res.text)["items"]

    data = []

    for store in store_list:
        store_number = store["id"]
        city = store["address"]["city"]
        state = store["address"]["stateOrRegion"]
        page_url = (
            "https://www.furniturerow.com/locations/"
            + city
            + "/"
            + state
            + "/"
            + store_number
        )
        hours_of_operation = store["dynamicProperties"]["stores"][0][
            "dynamicProperties"
        ]["hours"]
        location_name = store["name"]
        street_address = store["address"]["street1"] + " " + store["address"]["street2"]
        zip = store["address"]["postalCode"]
        country_code = store["address"]["country"]
        phone = store["contactInformation"]["phoneNumber"]
        location_type = store["locationType"]
        latitude = store["coordinates"]["latitude"]
        longitude = store["coordinates"]["longitude"]

        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
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


if __name__ == "__main__":
    scrape()
