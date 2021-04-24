from sgrequests import SgRequests
import csv
import re


def fetch_data():
    output = []
    locator_url = "https://www.c21.ca"
    url = "https://svc.moxiworks.com/service/profile/v2_insecure/offices/search?company_uuid=3341197&order_by=random&site_owner_uuid=0d4b737d-ba75-4fef-96db-11c81c493067&site_type=Brokerage%20Website"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    response = SgRequests().get(url, headers=headers)
    data = response.json()["data"]["result_list"]
    for row in data:
        currentrow = []
        address = row["location"]
        currentrow.append(locator_url)
        currentrow.append(url)
        currentrow.append(row["name"])
        currentrow.append(address["address"])
        currentrow.append(address["city"])
        currentrow.append(address["state"])
        currentrow.append(address["zip"])
        currentrow.append(address["country_code"])
        currentrow.append(row["uuid"])
        phone = row["phone"]
        phone = re.findall("[0-9]+", phone)
        phone = "".join(phone)
        if len(phone) == 10:
            currentrow.append(row["phone"])
        else:
            currentrow.append("<MISSING>")
        currentrow.append("<MISSING>")
        currentrow.append(address["latitude"])
        currentrow.append(address["longitude"])
        currentrow.append("<MISSING>")
        currentrow = ["<MISSING>" if point is None else point for point in currentrow]
        output.append(currentrow)
    return output


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
