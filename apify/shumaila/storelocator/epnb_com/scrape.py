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
    url = "https://www.epnb.com/about-enb/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select('a:contains("Branch Details")')
    p = 0
    for link in linklist:
        link = link["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1").text.strip().replace(" Branch Office", "")
        street = soup.find("div", {"class": "street-address"}).text
        city, state = soup.find("div", {"class": "city-state-zip"}).text.split(", ", 1)
        state, pcode = state.lstrip().split(" ", 1)
        ltype = soup.find("div", {"class": "location-atm"}).text
        if "ATM Available" in ltype:
            ltype = "Branch|ATM"
        else:
            ltype = "Branch"
        phone = soup.find("div", {"class": "phone-number"}).find("a").text
        hours = soup.find("div", {"class": "location-hours"}).text
        lat = soup.find("div", {"class": "marker"})["data-lat"]
        longt = soup.find("div", {"class": "marker"})["data-lng"]
        hourlist = hours.replace("\xa0", " ").strip().split("Day:")[1:]

        if "Drive-Up" in title:
            hours = ""
            for hr in hourlist:

                try:
                    hours = (
                        hours
                        + hr.split("Drive", 1)[0]
                        + " "
                        + hr.split("Drive", 1)[1].split("Hours:", 1)[1].strip()
                        + " "
                    )
                except:
                    hours = "<MISSING>"
        else:
            hours = ""
            for hr in hourlist:

                try:
                    hours = (
                        hours
                        + hr.split("Lobby", 1)[0]
                        + " "
                        + hr.split("Lobby Hours:", 1)[1].split("Drive", 1)[0].strip()
                        + " "
                    )
                except:
                    hours = "<MISSING>"
        data.append(
            [
                "https://www.epnb.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                ltype,
                lat,
                longt,
                hours.strip(),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
