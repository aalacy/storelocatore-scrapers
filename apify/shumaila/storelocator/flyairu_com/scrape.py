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
    url = "https://flyairu.com/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"class": "location-column"}).findAll("a")
    p = 0
    for div in divlist:
        link = div["href"]
        if "#" in link:
            continue
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        address = soup.find("address")
        address = re.sub(cleanr, "\n", str(address))
        address = re.sub(pattern, "\n", str(address)).strip().splitlines()
        street = address[0]
        city, state = address[1].split(", ", 1)
        state, pcode = state.split(" ", 1)
        phone = soup.find("div", {"class": "phone"}).text.replace("\n", "").strip()
        hrlink = (
            "https://www.airu-longview.com"
            + soup.find("div", {"class": "hours"}).find("a")["href"]
        )
        r = session.get(hrlink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = (
            soup.find("table", {"class": "hours_table"}).text.replace("\n", " ").strip()
        )
        title = div.text
        data.append(
            [
                "https://www.airu-longview.com",
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
