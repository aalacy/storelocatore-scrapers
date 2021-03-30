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
    url = "https://www.strawhatpizza.com/locations/index.php"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"class": "stores"}).findAll("div", {"class": "store"})

    p = 0
    for div in divlist:
        title = div.find("h3").text.replace("\n", "").strip()
        address = div.find("div", {"class": "address"})
        if "OPENING SOON!" in address.text:
            continue
        address = re.sub(cleanr, "\n", str(address)).strip().splitlines()
        m = 0
        street = address[m]
        m += 1
        try:
            city, state = address[m].split(", ", 1)
        except:
            street = street + " " + address[m]
            m += 1
            city, state = address[m].split(", ", 1)
        state, pcode = state.lstrip().split(" ", 1)

        m += 1
        phone = address[m]
        link = "https://www.strawhatpizza.com" + div.find("h3").find("a")["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = (
            soup.find("div", {"id": "hours"})
            .text.replace("Hours", "")
            .replace("pm", "pm ")
            .replace("day", "day ")
            .replace("\r", " ")
            .replace("-", " - ")
            .strip()
        )
        lat, longt = (
            soup.find("div", {"id": "storeMap"})
            .find("img")["src"]
            .split("center=", 1)[1]
            .split("&", 1)[0]
            .split("%2C", 1)
        )
        try:
            hours = hours.split(
                "For ",
            )[0]
        except:
            pass
        try:
            hours = hours.split(
                "We ",
            )[0]
        except:
            pass
        try:
            hours = hours.split(
                "NOW ",
            )[0]
        except:
            pass
        try:
            hours = hours.split(
                "Fax ",
            )[0]
        except:
            pass
        try:
            hours = hours.split(
                "ORDER ",
            )[0]
        except:
            pass
        data.append(
            [
                "https://www.strawhatpizza.com/",
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
