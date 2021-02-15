from bs4 import BeautifulSoup
import csv
import json

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
    url = "https://industrialbarreandride.com/locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.findAll("h2")[1].text
    phone = r.text.split('"contactPhoneNumber":"', 1)[1].split('"', 1)[0]
    address = r.text.split('"location":', 1)[1].split("}", 1)[0]
    address = address + "}"
    address = json.loads(address)
    street = address["addressTitle"]
    city, state = address["addressLine2"].split(", ")
    state, pcode = state.split(" ", 1)
    lat = r.text.split("mapLat&quot;:", 1)[1].split(",", 1)[0]
    longt = r.text.split("mapLng&quot;:", 1)[1].split(",", 1)[0]

    data.append(
        [
            "https://industrialbarreandride.com/",
            url,
            title,
            street,
            city,
            state,
            pcode,
            "US",
            "<MISSING>",
            phone,
            "<MISSING>",
            lat,
            longt,
            "<MISSING>",
        ]
    )

    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
