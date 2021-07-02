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
    pattern = re.compile(r"\s\s+")
    url = "https://www.rebeccataylor.com/our-stores/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    store_list = soup.select('a:contains("Details")')
    p = 0
    for st in store_list:
        if "https://www.rebeccataylor.com" in st["href"]:
            link = st["href"]
        else:
            link = "https://www.rebeccataylor.com" + st["href"]
        r = session.get(link, headers=headers, verify=False, timeout=100)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h2", {"class": "card-title"}).text
        address = (
            soup.find("div", {"class": "directions"}).text.strip().split("\n", 1)[0]
        )
        try:
            lat, longt = (
                soup.find("div", {"class": "directions"})
                .find("a")["href"]
                .split("@", 1)[1]
                .split("data", 1)[0]
                .split(",", 1)
            )
            longt = longt.split(",", 1)[0]
        except:
            lat = longt = "<MISSING>"
        try:
            hours = soup.find("div", {"class": "card-info"}).find("ul").text
            hours, phone = hours.split("TEL", 1)
            hours = re.sub(pattern, " ", hours).replace("\n", " ").strip()
            phone = phone.split("\n", 1)[0].split(": ", 1)[1]
        except:
            continue
        ltype = "Store"
        if "Outlet" in title:
            ltype = "Outlet"
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
        data.append(
            [
                "https://www.rebeccataylor.com/",
                link,
                title,
                street.strip().replace(",", ""),
                city.strip().replace(",", ""),
                state.strip(),
                pcode.strip().replace(".", ""),
                "US",
                "<MISSING>",
                phone.rstrip(),
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
