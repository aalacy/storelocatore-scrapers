from bs4 import BeautifulSoup
import csv
import usaddress
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
    pattern = re.compile(r"\s\s+")
    url = "https://www.cermakfreshmarket.com/our-stores"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "col-md-3"})
    p = 0
    for div in divlist:
        if "Coming Soon" in div.text:
            continue
        title = div.find("a").text
        link = "https://www.cermakfreshmarket.com" + div.find("a")["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            longt, lat = (
                soup.find("iframe")["src"]
                .split("!2d", 1)[1]
                .split("!3m", 1)[0]
                .split("!3d", 1)
            )
        except:
            lat = longt = "<MISSING>"
        soup = soup.text
        try:
            address = (
                soup.split("Located", 1)[1]
                .split("Phone", 1)[0]
                .strip()
                .replace("\n", " ")
            )
            phone = (
                soup.split("Phone", 1)[1]
                .split("Hours", 1)[0]
                .replace("\n", "")
                .replace(":", "")
                .strip()
            )
            hours = soup.split("Hours", 1)[1].split("\n", 1)[1].split("\n", 1)[0]
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
            if len(phone) < 3:
                phone = "<MISSING>"
        except:
            content = re.sub(cleanr, "\n", str(div))
            content = re.sub(pattern, "\n", content).strip().splitlines()
            street = content[-4]
            city, pcode = content[-3].split(" ", 1)
            phone = content[-2].replace("Phone: ", "")
            hours = content[-1]
            state = "IL"
            lat = longt = "<MISSING>"
        if len(city) < 3 and "Chicago" in street:
            street = street.replace("Chicago", "")
            city = "Chicago"
        data.append(
            [
                "https://www.cermakfreshmarket.com/",
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
