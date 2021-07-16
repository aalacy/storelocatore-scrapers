from bs4 import BeautifulSoup
import csv
import re
import usaddress
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
    url = "https://eggsupgrill.com/"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("div", {"id": "nav-locations"}).findAll("a")

    for link in linklist:
        link = link["href"]
        if link.find("new-stores-opening") > -1:
            break
        m = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(m.text, "html.parser")
        divlist = soup.findAll("div", {"class": "location-container"})

        for div in divlist:
            title = div.find("h3").text.lstrip().rstrip()
            address = div.findAll("p", {"class": "address"})[1]
            address = re.sub(cleanr, " ", str(address)).lstrip()

            phone = div.find("p", {"class": "phone"}).text
            hours = div.find("p", {"class": "hours"}).text

            lat = "<MISSING>"
            longt = "<MISSING>"
            try:
                coord = (
                    div.find("p", {"class": "directions"})
                    .find("a")["href"]
                    .split("/@")[1]
                    .split("/data")[0]
                )
                lat, longt = coord.split(",", 1)
                longt = longt.split(",", 1)[0]
            except:
                try:
                    coord = div.find("p", {"class": "directions"}).find("a")["href"]
                    m1 = session.get(coord, headers=headers, verify=False)
                    coord = m1.url
                    lat, longt = coord.split("/@")[1].split("/data")[0].split(",", 1)
                    longt = longt.split(",", 1)[0]
                except:
                    try:
                        lat = m.text.split('data-lat="', 1)[1].split('"', 1)[0]
                        longt = m.text.split('data-lng="', 1)[1].split('"', 1)[0]
                    except:
                        lat = "<MISSING>"
                        longt = "<MISSING>"
            address = usaddress.parse(address)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if (
                    temp[1].find("Address") != -1
                    or temp[1].find("Street") != -1
                    or temp[1].find("Recipient") != -1
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("BuildingName") != -1
                    or temp[1].find("USPSBoxType") != -1
                    or temp[1].find("USPSBoxID") != -1
                ):
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1
            street = street.lstrip().replace(",", "")
            state = state.lstrip().replace(",", "")
            city = city.lstrip().replace(",", "")
            pcode = pcode.lstrip().replace(",", "")
            if len(pcode) < 3:
                pcode = "<MISSING>"
            try:
                city, state = title.split(", ", 1)
            except:
                pass
            try:
                pcode = pcode.lstrip().split(" ", 1)[0]
            except:
                pass
            try:
                state = state.lstrip().split(" ")[0]
            except:
                pass
            phone = phone.replace("-EGGS (3447)", "-3447")
            if "North" in city:
                city = city.replace("North ", "").strip()
                street = street + " North"
            data.append(
                [
                    "https://eggsupgrill.com",
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
                    hours.replace("AM", " AM ")
                    .replace("PM", " PM ")
                    .replace(", MEETING ROOM AVAILABLE", ""),
                ]
            )

            p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
