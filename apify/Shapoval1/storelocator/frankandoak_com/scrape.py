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

    locator_domain = "https://www.frankandoak.com"
    api_url = "https://api.frankandoak.com/v3/cms/api/collections/get/retailLocations/?token=41a3f635cc5bfdfc22a744e3215215&fieldsFilter[]&countryAvailability=USA&lang=en"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "application/json",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "Authorization": "Bearer xgqj2svoTVR7DNcy5PjHjNNLYoacUWf3gQFo2fI2",
        "Origin": "https://www.frankandoak.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }
    data = '{"filter":{"active":true},"language":"en"}'
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["entries"]

    for j in js:
        page_url = f"https://www.frankandoak.com/stores/{j.get('url')}"
        location_name = j.get("name")
        location_type = j.get("storeType")
        street_address = j.get("address")
        phone = j.get("phone")
        state = j.get("province")
        postal = j.get("zip")
        country_code = j.get("country")
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        tmp = []
        for d in days:
            day = d
            time = j.get("hours").get(f"{d}")
            line = f"{day} {time}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp)
        if hours_of_operation.count("closed") == 7:
            hours_of_operation = "Closed"

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
