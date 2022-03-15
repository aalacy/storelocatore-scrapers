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

    items = []

    token_url = "https://api.ordercloud.io/oauth/token"
    body = "grant_type=client_credentials&client_id=98B2F232-8F53-43FB-865C-5F385BED413A&scope=MeAddressAdmin MeAdmin MeCreditCardAdmin MeXpAdmin Shopper SupplierReader SupplierAddressReader PasswordReset BuyerReader DocumentReader"
    response = session.post(token_url, data=body)
    data = json.loads(response.text)
    token = data["access_token"]

    DOMAIN = "playitagainsports.com"
    all_locations_url = "https://api.ordercloud.io/v1/suppliers?pageSize=100&page=1&Active=true&sortBy=Name"

    hdr = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Authorization": "Bearer {}".format(token),
        "Connection": "keep-alive",
        "Host": "api.ordercloud.io",
        "Origin": "https://www.playitagainsports.com",
        "Referer": "https://www.playitagainsports.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    }
    response = session.get(all_locations_url, headers=hdr)
    data = json.loads(response.text)
    all_items = []
    for location_data in data["Items"]:
        all_items.append(location_data)

    total_pages = data["Meta"]["TotalPages"]
    if total_pages > 1:
        page_num = data["Meta"]["Page"]
        while total_pages != page_num:
            for page in range(2, total_pages + 1):
                all_locations_url = "https://api.ordercloud.io/v1/suppliers?pageSize=100&page={}&Active=true&sortBy=Name".format(
                    str(page)
                )
                response = session.get(all_locations_url, headers=hdr)
                data = json.loads(response.text)
                for location_data in data["Items"]:
                    all_items.append(location_data)
                page_num = data["Meta"]["Page"]

    for location_data in all_items:
        location_details_url = (
            "https://api.ordercloud.io/v1/suppliers/{}/addresses/{}".format(
                location_data["ID"], location_data["ID"]
            )
        )
        location_response = session.get(location_details_url, headers=hdr)
        location_full_data = json.loads(location_response.text)

        store_url = "https://www.playitagainsports.com/locations/{}".format(
            location_data["xp"]["slug"]
        )
        location_name = location_full_data["CompanyName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = location_full_data["Street1"]
        if location_full_data["Street2"]:
            street_address += " " + location_full_data["Street2"]
        street_address = street_address if street_address else "<MISSING>"
        city = location_full_data["City"]
        city = city if city else "<MISSING>"
        state = location_full_data["State"]
        state = state if state else "<MISSING>"
        zip_code = location_full_data["Zip"]
        zip_code = zip_code.strip() if zip_code else "<MISSING>"
        country_code = location_full_data["Country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = location_full_data["ID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = location_full_data["Phone"]
        phone = phone.replace(" (PIAS)", "") if phone else "<MISSING>"
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
