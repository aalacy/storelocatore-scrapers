import csv
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tonysfreshmarket_com")

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
    # Your scraper here
    final_data = []
    url = "https://api.freshop.com/1/stores?app_key=tony_s_fresh_market&fields=id%2Cname&has_address=true&token=63d13ad03d4393eadec47baecda1e382"
    r = session.get(url, headers=headers, verify=False)
    name_list = r.text.split('"items":')[1].split("]", 1)[0]
    name_list = name_list + "]"
    name_list = json.loads(name_list)

    url1 = "https://api.freshop.com/1/stores?app_key=tony_s_fresh_market&fields"
    r1 = session.get(url1, headers=headers, verify=False)
    linklist = r1.text.split('"items":')[1].split("]}", 1)[0]
    linklist = linklist + "]"
    linklist = json.loads(linklist)

    for name in name_list:
        for link in linklist:
            if name["name"] == link["name"]:
                title = link["name"]
                store = link["id"]
                lat = link["latitude"]
                longt = link["longitude"]
                city = link["city"]
                state = link["state"]
                pcode = link["postal_code"]
                phone = link["phone"]
                hours = link["hours_md"]
                phone = link["phone_md"]
                phone = phone.split("\nFax:", 1)[0]
                phone = phone.strip()
                try:
                    street = link["address_0"] + " " + link["address_1"]
                except:
                    street = link["address_1"]
        final_data.append(
            [
                "https://www.tonysfreshmarket.com/",
                "https://www.tonysfreshmarket.com/my-store/store-locator",
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
    return final_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
