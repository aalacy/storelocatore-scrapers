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
    url = "https://flightadventurepark.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "single_locations"})
    p = 0
    for div in divlist:
        store = div["id"].replace("loc_", "")
        title = div.find("h2").text
        address = div.find("p", {"class": "adds"}).text
        try:
            street, city, state, pcode = address.split(", ")
        except:
            street, temp, city, state, pcode = address.split(", ")
            street = street + " " + temp
        phone = div.find("p", {"class": "tel"}).text.replace("\n", "").strip()
        link = div.find("a")["onclick"].replace("goToPark('", "").replace("')", "")
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = (
            soup.findAll("div", {"class": "adds"})[-1]
            .text.strip()
            .replace("/", "")
            .replace("Hours", "")
            .replace("\n", "")
            .replace("pm", "pm ")
            .replace("PM", "PM ")
            .replace("CLOSED", "CLOSED ")
            .strip()
        )

        data.append(
            [
                "https://flightadventurepark.com/",
                link,
                title,
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
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
