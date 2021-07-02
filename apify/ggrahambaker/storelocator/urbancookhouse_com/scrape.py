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
    url = "https://www.urbancookhouse.com/location/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "location-info"})
    p = 0
    for div in divlist:

        title = div.find("span", {"class": "location-title"}).text.strip()

        try:
            lat, longt = (
                div.find("span", {"class": "address"})
                .find("a")["href"]
                .split("@", 1)[1]
                .split("data", 1)[0]
                .split(",", 1)
            )
            longt = longt.split(",", 1)[0]
            address = div.find("span", {"class": "address"}).find("a")
            address = re.sub(cleanr, "\n", str(address))
            address = re.sub(pattern, "\n", str(address)).strip().splitlines()

            street = address[0]
            city, state = address[1].split(", ", 1)
            state, pcode = state.split(" ", 1)
        except:
            lat = longt = "<MISSING>"
            address = div.find("span", {"class": "address"})
            address = re.sub(cleanr, "\n", str(address))
            address = re.sub(pattern, "\n", str(address)).strip().splitlines()

            street = address[3]
            city, state = address[4].split(", ", 1)
            state, pcode = state.split(" ", 1)
        phone = (
            div.find("span", {"class": "location-phone"})
            .text.strip()
            .split("\n", 1)[0]
            .replace("phone ", "")
        )
        try:
            hours = (
                div.find("span", {"class": "hours"})
                .text.replace("\n", " ")
                .replace("\t", "")
                .replace("pm", "pm ")
                .replace("\r", "")
                .replace("Dine-In: ", "")
                .replace("Hours ", "")
                .strip()
            )
        except:
            hours = "<MISSING>"
        try:
            hours = hours.split("Available", 1)[0]
        except:
            pass
        try:
            hours = hours.split("(", 1)[0]
        except:
            pass
        data.append(
            [
                "https://www.urbancookhouse.com/",
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
                hours,
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
