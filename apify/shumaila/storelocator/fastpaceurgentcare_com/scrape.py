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
    # Your scraper here
    data = []
    streetlist = []
    p = 0
    url = "https://www.fastpacehealth.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    soup = str(soup)
    start = 0
    while True:

        start = soup.find('\\"Title\\"', start)
        if start == -1:
            break
        start = soup.find(":", start) + 1
        end = soup.find(",", start)
        title = soup[start:end].replace("\\", "").replace('"', "")
        start = end + 1
        start = soup.find('\\"LocationNumber\\"', start)
        start = soup.find(":", start) + 1
        end = soup.find(",", start)
        store = soup[start:end].replace("\\", "").replace('"', "")
        start = end + 1
        start = soup.find('\\"DirectUrl\\"', start)
        start = soup.find(":", start) + 1
        end = soup.find(",", start)
        link = "https://www.fastpacehealth.com" + soup[start:end].replace(
            "\\", ""
        ).replace('"', "").replace(" ", "-")
        start = end + 1
        start = soup.find('\\"LocationAddress\\"', start)
        start = soup.find(":", start)
        start = soup.find('"', start) + 1
        end = soup.find('"', start)
        address = soup[start:end].replace("\\", "").replace(",", "")
        if address.find("COMING SOON") == -1:

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
            start = end + 1
            start = soup.find('\\"LocationPhoneNum\\"', start)
            start = soup.find(":", start) + 1
            end = soup.find(",", start)
            phone = soup[start:end].replace("\\", "").replace('"', "")
            start = end + 1
            start = soup.find('\\"Latitude\\"', start)
            start = soup.find(":", start) + 1
            end = soup.find(",", start)
            lat = soup[start:end].replace("\\", "").replace('"', "")
            start = end + 1
            start = soup.find('\\"Longitude\\"', start)
            start = soup.find(":", start) + 1
            end = soup.find(",", start)
            longt = soup[start:end].replace("\\", "").replace('"', "")
            start = end + 1

            r1 = session.get(link, headers=headers, verify=False)
            soup1 = str(BeautifulSoup(r1.text, "html.parser"))

            mstart = soup1.find("Hours of Operation")
            mstart = soup1.find('"Values\\"', mstart)
            mstart = soup1.find("[", mstart) + 1
            mend = soup1.find("]", mstart)
            hours = (
                soup1[mstart:mend].replace("\\", "").replace('"', "").replace(",", ", ")
            )

            if len(hours) < 3:
                hours = "<MISSING>"
            if street.lstrip() in streetlist:
                continue
            streetlist.append(street.lstrip())
            if len(pcode) < 3:
                pcode = "<MISSING>"
            if "Tennessee" in city and len(state) < 2:
                state = "TN"
                city = city.replace("Tennessee", "")
            if len(phone) < 3:
                phone = "<MISSING>"
            data.append(
                [
                    "https://fastpaceurgentcare.com/",
                    link,
                    title,
                    street.lstrip(),
                    city.lstrip(),
                    state.lstrip(),
                    pcode.lstrip(),
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours,
                ]
            )

            p += 1
        else:
            start = end + 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
