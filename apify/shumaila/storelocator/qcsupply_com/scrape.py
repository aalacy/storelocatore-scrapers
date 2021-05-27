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
    p = 0
    url = "https://www.qcsupply.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "amlocator-store-desc"})
    for div in divlist:
        link = "https://www.qcsupply.com" + div.find(
            "span", {"class": "location_link"}
        ).find("span")["onclick"].split("=", 1)[1].replace("'", "")
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        street = (
            soup.findAll("div", {"class": "location-address-inner"})[0]
            .findAll("span", {"class": "address-line"})[0]
            .text
        )

        city, state = (
            soup.findAll("div", {"class": "location-address-inner"})[0]
            .findAll("span", {"class": "address-line"})[1]
            .text.replace("\xa0", " ")
            .strip()
            .split(", ", 1)
        )
        state, pcode = state.split(" ", 1)

        phone = soup.select_one("a[href*=tel]").text
        hours = (
            soup.findAll("div", {"class": "location-address-inner"})[-2]
            .text.replace("\n", " ")
            .replace("\xa0", " ")
            .strip()
        )
        title = city + ", " + state
        try:
            lat, longt = r.text.split("LatLng(", 1)[1].split(")", 1)[0].split(",", 1)
        except:
            lat = longt = "<MISSING>"
        data.append(
            [
                "https://www.qcsupply.com/",
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
