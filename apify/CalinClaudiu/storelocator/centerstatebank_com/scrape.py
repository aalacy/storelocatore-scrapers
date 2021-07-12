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
    titlelist = []
    url = "https://southstatebank.com/Global/About/CRA/Locations-Listing"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=location-detail]")

    p = 0
    for link in linklist:
        if "https://southstatebank.com/" in link["href"]:
            link = link["href"]
        else:
            link = "https://southstatebank.com" + link["href"]
        if link in titlelist:
            continue
        titlelist.append(link)
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1").text.strip()
        street = soup.find("div", {"class": "address"}).findAll("p")[0].text
        city, state = (
            soup.find("div", {"class": "address"}).findAll("p")[1].text.split(", ", 1)
        )
        state, pcode = state.split(" ", 1)
        hours = (
            soup.text.split("Location Hours", 1)[1]
            .split("Drive Up ATM", 1)[0]
            .replace("\n", " ")
            .strip()
        )
        phone = soup.find("div", {"class": "contact"}).findAll("a")[1].text
        lat = (
            soup.find("div", {"class": "detail-map"})["data-initdata"]
            .split('"Lat":', 1)[1]
            .split(",", 1)[0]
        )
        longt = (
            soup.find("div", {"class": "detail-map"})["data-initdata"]
            .split('"Lng":', 1)[1]
            .split("}", 1)[0]
        )
        if "Branch Features" in soup.text:
            ltype = "Branch | ATM"
        else:
            ltype = "ATM"
        try:
            hours = hours.split("Walk Up ATM", 1)[0]
        except:
            pass
        try:
            hours = hours.split("Branch Features", 1)[0]
        except:
            pass
        street = city
        city = state.replace(",", "")
        state, pcode = pcode.split(" ", 1)
        if len(state) > 3:
            city = city + " " + state.replace(",", "")
            state, pcode = pcode.split(" ", 1)
        if pcode.isdigit():
            pass
        else:
            city = city + " " + state
            state, pcode = pcode.split(" ", 1)
        if len(state) > 3:
            city = city + " " + state.replace(",", "")
            state, pcode = pcode.split(" ", 1)
        store = link.split("/")[-2]
        data.append(
            [
                "https://centerstatebank.com/",
                link,
                title,
                street,
                city.replace(",", ""),
                state,
                pcode,
                "US",
                store,
                phone,
                ltype,
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
