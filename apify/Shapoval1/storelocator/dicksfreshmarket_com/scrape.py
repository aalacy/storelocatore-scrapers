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

    locator_domain = "https://dicksfreshmarket.com"
    api_url = "https://dicksfreshmarket.com/ajax/index.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Referer": "https://dicksfreshmarket.com/contact",
    }

    data = {
        "method": "POST",
        "apiurl": "https://dicksfreshmarket.rsaamerica.com/Services/SSWebRestApi.svc/GetClientStores/1",
    }

    r = session.post(api_url, headers=headers, data=data)
    js = r.json()
    for j in js["GetClientStores"]:

        page_url = "https://dicksfreshmarket.com/contact"
        location_name = j.get("ClientStoreName")
        location_type = "<MISSING>"
        street_address = j.get("AddressLine1")
        phone = j.get("StorePhoneNumber")
        state = j.get("StateName")
        postal = j.get("ZipCode")
        country_code = "US"
        city = j.get("City")
        store_number = j.get("StoreNumber")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        hours_of_operation = j.get("StoreTimings")

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
