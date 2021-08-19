import csv
from sgrequests import SgRequests


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


def fetch_data():
    out = []

    locator_domain = "https://www.givemelibertyburger.com"
    api_url = "https://www.givemelibertyburger.com/graphql"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.givemelibertyburger.com/",
        "content-type": "application/json",
        "Origin": "https://www.givemelibertyburger.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }
    data = '{"operationName":"restaurantWithLocations","variables":{"restaurantId":9257},"extensions":{"operationId":"PopmenuClient/c669dd1a7a1023c80eeb314ed94b042f"}}'
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["data"]["restaurant"]["locations"]
    for j in js:

        page_url = "https://www.givemelibertyburger.com/"
        location_name = j.get("name")
        location_type = "Restaurant"
        street_address = j.get("streetAddress")
        phone = j.get("phone")
        state = j.get("state")
        postal = j.get("postalCode")
        country_code = j.get("country")
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = " ".join(j.get("schemaHours"))

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
