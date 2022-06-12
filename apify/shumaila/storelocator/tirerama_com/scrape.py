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
    url = "https://www.tirerama.com/Locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "loclisting"})
    p = 0
    for div in divlist:
        content = div.find("div", {"class": "locationInfo"}).text
        content = re.sub(pattern, "\n", content).strip().splitlines()
        title = content[0]
        street = content[1]
        city, state = content[2].split(", ", 1)
        state, pcode = state.strip().split(" ", 1)
        phone = div.find("div", {"class": "locphone"}).text
        hours = div.find("div", {"class": "locationhours"}).text
        lat = div.find("p", {"class": "locationdirections"}).find("span")["lat"]
        longt = div.find("p", {"class": "locationdirections"}).find("span")["lon"]
        link = div.find("a", {"class": "DetailLink"})["href"]
        hours = hours.replace("\n", " ").replace("\r", " ").replace("Hours", "").strip()
        hours = re.sub(pattern, " ", hours).strip()
        data.append(
            [
                "https://www.tirerama.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone.replace("\n", "").strip(),
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
