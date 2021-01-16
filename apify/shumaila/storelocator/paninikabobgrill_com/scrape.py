from bs4 import BeautifulSoup
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
    url = "https://paninikabobgrill.com/wp-admin/admin-ajax.php?action=store_search&lat=34.05223&lng=-118.24368&max_results=25&search_radius=50&autoload=1"
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()
    for loc in loclist:
        title = loc["store"]
        store = loc["id"]
        street = loc["address"] + " " + str(loc["address2"])
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        phone = str(loc["phone"])
        if len(phone) < 2:
            phone = "<MISSING>"
        lat = loc["lat"]
        longt = loc["lng"]
        link = "https://paninikabobgrill.com" + loc["url"]
        hours = BeautifulSoup(loc["hours"], "html.parser").text
        data.append(
            [
                "https://paninikabobgrill.com/",
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
                hours.replace("PM", "PM ").replace("day", "day "),
            ]
        )
        p += 1
    data.append(
        [
            "https://paninikabobgrill.com/",
            "https://paninikabobgrill.com/locations/riverside/",
            "Riverside",
            "1298 Galleria at Tyler G121",
            "Riverside",
            "CA",
            "92503",
            "US",
            "<MISSING>",
            "(951) 352-6318",
            "<MISSING>",
            "33.90923",
            "-117.45734",
            "Mon – Sun: 10:00am to 9:00pm",
        ]
    )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
