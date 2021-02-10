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
    p = 0
    url = "https://behandpicked.com/handpicked-stores/"
    r = session.get(url, headers=headers, verify=False)

    soup = BeautifulSoup(r.text, "html.parser")

    titlelist = soup.find("div", {"class": "category-banner-section"}).findAll("strong")
    divlist = soup.find("div", {"class": "category-banner-section"}).text
    for i in range(0, len(titlelist) - 1):
        content = (
            divlist.split(titlelist[i].text)[1]
            .split(titlelist[i + 1].text)[0]
            .replace(":", "")
            .lstrip()
            .replace("\n", " ")
            .strip()
        )
        address = content.split("Phone", 1)[0].replace(":", "").lstrip()
        phone = (
            content.split("Phone", 1)[1].split("E-mail", 1)[0].replace(":", "").lstrip()
        )
        phone = phone.split("Hour", 1)[0].replace(":", "").lstrip()
        hours = content.split("Hours", 1)[1].split("Th", 1)[0].replace(":", "").lstrip()
        try:
            hours = hours.split("Loc", 1)[0].replace(":", "").lstrip()
        except:
            pass
        try:
            hours = hours.split("E-mail", 1)[0].strip()
        except:
            pass
        title = titlelist[i].text

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

        data.append(
            [
                "https://behandpicked.com/",
                "https://behandpicked.com/handpicked-stores/",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone.replace(": ", ""),
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours.replace(": ", "").replace("&amp;", "-"),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
