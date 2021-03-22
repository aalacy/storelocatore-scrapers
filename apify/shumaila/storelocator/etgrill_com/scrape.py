from bs4 import BeautifulSoup
import csv
import re

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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.etgrill.com/hours-location/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    address = soup.find("a", {"class": "address"})
    address = re.sub(cleanr, "\n", str(address)).strip().splitlines()
    street = address[0]
    city, state = address[1].split(", ", 1)
    lat, longt = (
        soup.find("a", {"class": "address"})["href"].split("=", 1)[1].split(",")
    )
    phone = soup.select_one("a[href*=tel]").text
    hours = soup.find("div", {"class": "hours"}).text
    hours = re.sub(pattern, " ", hours).replace("\n", " ").strip()

    data.append(
        [
            "https://www.etgrill.com/",
            url,
            "El Torito Grill",
            street,
            city,
            state,
            "<MISSING>",
            "US",
            "<MISSING>",
            phone,
            "<MISSING>",
            lat,
            longt,
            hours,
        ]
    )

    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
