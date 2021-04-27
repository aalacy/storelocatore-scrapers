from bs4 import BeautifulSoup
import csv
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
    url = "https://www.beansandbrews.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("a", {"class": "location"})
    p = 0
    for div in divlist:
        link = div["href"]

        title = div.find("h4", {"class": "location__name"}).text.split("\n", 1)[0]
        address = (
            div.find("p", {"class": "location__address"})
            .text.replace("\n", " ")
            .strip()
        )
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
                or temp[1].find("Occupancy") != -1
                or temp[1].find("Recipient") != -1
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
        city = city.lstrip().replace(",", "")
        state = state.lstrip().replace(",", "")
        pcode = pcode.lstrip().replace(",", "")

        phone = div.find("p", {"class": "location__phone"}).text
        try:
            phone = phone.split(":", 1)[1].strip()
        except:
            pass
        hours = div.find("p", {"class": "location__hours"}).text.replace("\n", " ")
        try:
            hours = hours.split(":", 1)[1].strip()
        except:
            pass
        try:
            street = street.split(") ", 1)[1].strip()
        except:
            pass
        if len(phone) < 3:
            phone = "<MISSING>"
        if len(state) < 2:
            state = city
            city = title.split("-", 1)[0]
            street = street.replace(city, "").strip()
        if "Utah" in state:
            state = "UT"
        if "East" in city or "West" in city or "North" in city or "South" in city:
            if city.split(" ", 1)[0] in street.split(" ")[-1]:
                pass
            else:
                street = street + " " + city.split(" ", 1)[0]
            city = city.split(" ", 1)[1]
        data.append(
            [
                "https://www.beansandbrews.com/",
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
                hours.replace("\r", ""),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
