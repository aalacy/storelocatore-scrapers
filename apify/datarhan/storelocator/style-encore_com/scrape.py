import csv
import json

from sgrequests import SgRequests


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
    session = SgRequests()

    DOMAIN = "style-encore.com"
    post_url = "https://api.ordercloud.io/oauth/token"

    body = "grant_type=client_credentials&client_id=754A01E1-1BD5-4D9F-87E9-600B12CACA02&scope=MeAddressAdmin MeAdmin MeCreditCardAdmin MeXpAdmin Shopper SupplierReader SupplierAddressReader PasswordReset BuyerReader DocumentReader"
    t_res = session.post(post_url, data=body)
    data = json.loads(t_res.text)
    token = data["access_token"]

    hdr = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Authorization": "Bearer {}".format(token),
        "Connection": "keep-alive",
        "Host": "api.ordercloud.io",
        "Origin": "https://www.style-encore.com",
        "Referer": "https://www.style-encore.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    }

    items = []

    all_locations_url = "https://api.ordercloud.io/v1/suppliers?pageSize=80&page=1&Active=true&sortBy=Name"
    response = session.get(all_locations_url, headers=hdr)
    data = json.loads(response.text)

    for location_data in data["Items"]:
        if location_data["xp"]["status"] == "ComingSoon":
            continue
        location_details_url = (
            "https://api.ordercloud.io/v1/suppliers/{}/addresses/{}".format(
                location_data["ID"], location_data["ID"]
            )
        )
        location_response = session.get(location_details_url, headers=hdr)
        location_full_data = json.loads(location_response.text)

        store_url = "https://www.style-encore.com/locations/{}".format(
            location_data["xp"]["slug"]
        )
        location_name = location_full_data["CompanyName"]
        street_address = location_full_data["Street1"]
        street_address = street_address if street_address else "<MISSING>"
        city = location_full_data["City"]
        city = city if city else "<MISSING>"
        state = location_full_data["State"]
        state = state if state else "<MISSING>"
        zip_code = location_full_data["Zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = location_full_data["Country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = location_full_data["ID"]
        phone = location_full_data["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = location_data["xp"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = location_data["xp"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = location_full_data["xp"]["hours"]
        if hours_of_operation:
            hours_list = []
            for key, value in hours_of_operation.items():
                hours_list.append("{} - {}".format(key, value))
            hours_of_operation = ", ".join(hours_list)
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

        item = [
            DOMAIN,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
