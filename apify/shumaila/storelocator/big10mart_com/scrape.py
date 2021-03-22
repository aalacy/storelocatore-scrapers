from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
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
    url = "http://www.big10mart.com/locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "loc_link"})
    p = 0
    linklist = []
    for div in divlist:
        link = div.text
        if link in linklist:
            continue
        linklist.append(link)
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("div", {"class": "slideOfferSubTitle"}).text
        store = title.split("#", 1)[1].split("-", 1)[0]
        address = soup.select("a[href*=maplocation]")[-1].text.splitlines()
        street = address[0]
        city, state = address[1].split(", ")
        pcode = "<MISSING>"
        try:
            state, pcode = state.strip().split(" ", 1)
        except:
            pass
        phone = soup.select_one("a[href*=tel]").text

        hours = (
            soup.text.split("Hours", 1)[1]
            .split("location", 1)[0]
            .replace("\n", " ")
            .strip()
        )
        try:
            hours = hours.split("Hours ", 1)[1]
        except:
            pass
        data.append(
            [
                "http://www.big10mart.com/",
                link,
                title.replace("\xa0", ""),
                street.replace("\xa0", ""),
                city.replace("\xa0", ""),
                state.replace("\xa0", ""),
                pcode.replace("\xa0", ""),
                "US",
                store,
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours.replace("\xa0", ""),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
