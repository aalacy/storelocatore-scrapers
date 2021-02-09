import csv
from sgrequests import SgRequests

session = SgRequests()
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("consulatehealthcare_com")


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "cache-control": "no-cache",
        "Authorization": "YNDRAXWGIEKBMEAP",
    }
    # 17.402260273552102,-69.71870312499948,58.77346001357117,-122.27729687499975
    # bounding box ('United States', (-171.791110603, 18.91619, -66.96466, 71.3577635769)),

    center = "45.13697678845,-119.3778853015"
    bbox = "18.91619,-66.96466,71.3577635769,-171.791110603"
    url = (
        "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=YNDRAXWGIEKBMEAP&center="
        + center
        + "&coordinates="
        + bbox
        + "&multi_account=false&page=1&pageSize=5000"
    )
    response = session.get(url, headers=headers).json()
    for data in response:
        locator_domain = "http://consulatehealthcare.com/"
        street_address = data["store_info"]["address"]
        page_url = "https://centers.consulatehealthcare.com" + data["llp_url"]
        city = data["store_info"]["locality"]
        zipp = data["store_info"]["postcode"]
        state = data["store_info"]["region"]
        location_name = data["store_info"]["name"]
        phone = data["store_info"]["phone"]
        latitude = data["store_info"]["latitude"]
        longitude = data["store_info"]["longitude"]
        store_number = data["store_info"]["corporate_id"]
        country_code = data["store_info"]["country"]
        hours_of_operation = "<MISSING>"
        location_type = "<MISSING>"
        store = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zipp,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
            page_url,
        ]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
