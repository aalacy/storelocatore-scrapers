from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("greatwraps_com")

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
    url = "https://www.greatwraps.com/locations-list/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("a", {"class": "textlink"})
    for link in linklist:
        url = "https://www.greatwraps.com" + link["href"]
        p = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(p.text, "html.parser")
        title = soup.find("div", {"id": "locName"})
        title = title.text.strip()
        phone = soup.find("a", {"class": "globalBtn red phone"})
        if phone is None:
            phone = "<MISSING>"
        else:
            phone = phone.text.strip()
        Address = soup.find("p", {"class": "locationsAddress"}).text.strip()
        Address = Address.rstrip("United States").strip()
        if (
            url
            == "https://www.greatwraps.com/location-details/?stitle=Atlanta International Airport (ATL) Concourse C"
        ):
            street = "Airport location"
            city = "<MISSING>"
            state = "<MISSING>"
            pcode = "<MISSING>"
        elif (
            url
            == "https://www.greatwraps.com/location-details/?stitle=Chicago Premium Outlets"
        ):
            street = "Mall Location"
            city = "<MISSING>"
            state = "<MISSING>"
            pcode = "<MISSING>"
        else:
            Address = Address.rstrip(",")
            Address = Address.split(",")
            if len(Address) == 4:
                street = Address[0].strip() + " " + Address[1].strip()
                city = Address[2].strip()
                statenzip = Address[3].strip()
                statenzip = statenzip.strip()
            if len(Address) == 3:
                street = Address[0].strip()
                city = Address[1].strip()
                statenzip = Address[2].strip()
                statenzip = statenzip.strip()
            if len(statenzip) == 2:
                state = statenzip
                pcode = "<MISSING>"
            else:
                state = statenzip.split(" ")[0].strip()
                pcode = statenzip.split(" ")[1].strip()
        hours = soup.find("div", {"id": "locationsHours"})
        hours = hours.text.strip()
        hours = hours.replace("\n", " ")
        hours = hours.lstrip("Hours of Operation ")
        hours = hours.replace("Weekdays:", "Monday - Friday:")

        coords = soup.findAll("script")
        coord = str(coords[7])
        coord = coord.split("var latlng = new google.maps.LatLng(")[1].split(");")[0]
        if coord == ",":
            lat = "<MISSING>"
            lng = "<MISSING>"
        else:
            lat = coord.split(",")[0]
            lng = coord.split(",")[1]
        data.append(
            [
                "https://www.greatwraps.com/",
                url,
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
                lng,
                hours,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
