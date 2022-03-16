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
    url = "https://coppercellar.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select_one('li:contains("Locations")').find("ul").findAll("a")
    p = 0
    for div in divlist:
        title = div.text
        link = div["href"]
        if "private-dining" in link:
            continue
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        address = soup.text.split("Address", 1)[1].split("Call", 1)[0]
        try:
            address = address.split("Located", 1)[0]
        except:
            pass
        address = address.strip().splitlines()
        street = address[0]
        city, state = address[1].split(", ", 1)
        state, pcode = state.split(" ", 1)
        phone = soup.text.split("Phone", 1)[1].split("\n", 1)[0].strip()
        hours = (
            soup.text.split("Hours", 1)[1]
            .split("Holiday", 1)[0]
            .replace("\n", " ")
            .strip()
        )
        longt, lat = (
            soup.find("iframe")["src"]
            .split("!2d", 1)[1]
            .split("!2m", 1)[0]
            .split("!3d", 1)
        )

        data.append(
            [
                "https://coppercellar.com/",
                link,
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
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
