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
    url = "https://api.freshop.com/1/stores?app_key=food_country_usa&has_address=true&limit=-1&token=5f9dce09af2e3dcea65067e3617ebe22"
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()["items"]
    for loc in loclist:
        title = loc["name"]
        store = loc["store_number"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        street = loc["address_1"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["postal_code"]
        hours = loc["hours_md"].replace("\n", " ").strip()
        phone = loc["phone"]
        link = loc["url"]
        data.append(
            [
                "https://www.foodcountryusainc.com/",
                link,
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
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
