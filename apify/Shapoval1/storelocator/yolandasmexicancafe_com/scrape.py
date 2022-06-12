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

    locator_domain = "https://www.yolandasmexicancafe.com/"
    api_url = "https://www.yolandasmexicancafe.com/graphql"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "content-type": "application/json",
        "Origin": "https://www.yolandasmexicancafe.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }

    data = '{"operationName":"restaurantWithLocations","variables":{"restaurantId":9483},"extensions":{"operationId":"PopmenuClient/102b4a83f4a8183677ec8cb4829ac6ce"}}'
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["data"]["restaurant"]["locations"]

    for j in js:

        page_url = "https://www.yolandasmexicancafe.com/"
        location_name = j.get("name")
        location_type = "Restaurant"
        street_address = j.get("streetAddress") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        store_number = "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
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
