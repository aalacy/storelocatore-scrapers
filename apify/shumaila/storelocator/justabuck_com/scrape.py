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
    url = "https://www.justabuck.com/locations.asp"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select('a:contains("Details")')

    p = 0
    for div in divlist:
        link = "https://www.justabuck.com/" + div["href"]
        store = link.split("=", 1)[1]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        address = (
            soup.text.split("Address: ", 1)[1]
            .split("Phone", 1)[0]
            .replace("\xa0", " ")
            .strip()
        )
        street, city = address.split("\n", 1)
        city, state = city.replace("\n", "").split(",", 1)
        pcode = str(state).lstrip().split(" ")[-1]
        state = str(state).lstrip().split(" ")[0]
        phone = (
            soup.text.split("Phone", 1)[1]
            .split("\n", 1)[0]
            .replace(":", "")
            .replace("\xa0", "")
            .strip()
        )
        hours = soup.text.split("Hours: ", 1)[1].split("\n", 1)[0].strip()
        if "OPENING SOON" in hours:
            continue
        data.append(
            [
                "https://www.justabuck.com/",
                link,
                city,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours.replace("\r", " ").replace("\x96", "").strip(),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
