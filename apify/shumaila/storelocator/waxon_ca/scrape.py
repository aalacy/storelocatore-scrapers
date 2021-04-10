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
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    url = "https://waxon.ca/pages/waxing-near-me"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "location-container"})
    for div in divlist:
        title = div.find("h3").text.strip()
        address = re.sub(cleanr, "\n", str(div.find("address")))
        address = re.sub(pattern, "\n", str(address)).strip().splitlines()
        street = address[0].replace(" · ", " ").strip()
        try:
            city, state, pcode = address[1].split(", ")
        except:
            street = street + " " + address[1]
            city, state, pcode = address[2].split(", ")
        phone = div.find("a").text
        hours = (
            div.find("div", {"class": "location-hours"}).text.replace("\n", " ").strip()
        )
        if "SEE YOU SUMMER 2021" in hours or "Bar Tabs" in hours or "CLOSED" in phone:
            hours = "Temporarily closed"
            phone = "<MISSING>"
        try:
            street = street.split("(", 1)[0]
        except:
            pass
        data.append(
            [
                "https://waxon.ca",
                "https://waxon.ca/pages/waxing-near-me",
                title,
                street,
                city,
                state,
                pcode,
                "CA",
                "<MISSING>",
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
