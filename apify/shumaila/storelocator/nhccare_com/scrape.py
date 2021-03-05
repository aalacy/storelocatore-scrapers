from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests
import usaddress

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
    url = "https://nhccare.com/find-a-community/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.select("a[href*=-results]")
    p = 0
    for stnow in state_list:
        statelink = stnow["href"]
        r = session.get(statelink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.select("a[href*=locations]")
        for link in linklist:
            link = link["href"]
            if link in titlelist:
                continue
            titlelist.append(link)
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                address = soup.text.split("Address:", 1)[1].split("\n", 1)[0].strip()
                if "95 Laurel Street" in address:
                    address = (
                        soup.text.split("Address:", 1)[1].split("\n", 1)[0].strip()
                        + " "
                        + soup.text.split("Address:", 1)[1]
                        .split("\n")[1]
                        .split("\n")[0]
                        .strip()
                    )
            except:
                continue
            phone = soup.text.split("hone:", 1)[1].split("\n", 1)[0].strip()
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
            street = street.strip().replace(",", "")
            if street in titlelist:
                continue
            titlelist.append(street)
            city = city.strip().replace(",", "")
            state = state.strip().replace(",", "").replace(".", "")
            pcode = pcode.strip().replace(",", "").replace(".", "")

            try:
                lat, longt = (
                    soup.select_one("a[href*=maps]")
                    .split("@", 1)[1]
                    .split(",17")[0]
                    .split(",")
                )
            except:
                lat = longt = "<MISSING>"
            title = soup.find("h1").text
            data.append(
                [
                    "https://nhccare.com",
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
                    "<MISSING>",
                ]
            )
            p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
