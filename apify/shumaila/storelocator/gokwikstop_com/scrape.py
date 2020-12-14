import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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
    data = []
    url = "https://gokwikstop.com/wp-admin/admin-ajax.php?action=store_search&lat=42.529238&lng=-90.696285&max_results=25&search_radius=10&autoload=1"
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()
    for loc in loclist:
        street = loc["address"]
        title = loc["store"]
        store = loc["id"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        phone = loc["phone"]
        lat = loc["lat"]
        longt = loc["lng"]
        if len(phone) < 3:
            phone = "<MISSING>"
        data.append(
            [
                "https://gokwikstop.com/",
                "https://gokwikstop.com/store-locator/",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                "<MISSING>",
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
