from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress


logger = SgLogSetup().get_logger("thelube_com")

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
    url = "http://thelube.com/category/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("ul", {"class": "locationDetails"}).findAll(
        "li", {"class": "location"}
    )

    for div in divlist:
        link = div.find("a")["href"]
        title = div.find("h4").text
        address = div.find("span", {"class": "address"}).text
        store = div["id"].split("-")[1]
        phone = div.find("span", {"class": "phoneNum"}).text
        lat = div.find("span", {"class": "lat"}).text
        long = div.find("span", {"class": "long"}).text
        r1 = session.get(link, headers=headers, verify=False)
        soup1 = BeautifulSoup(r1.text, "html.parser")

        b = "()"
        for char in b:
            phone = phone.replace(char, "")
        hourslist = soup1.find("li", {"class": "clockIcon"}).text.splitlines()
        hours = ""
        for hr in hourslist:
            if hr.find("am") > -1 and hr.find("pm") > -1:
                hours = hours + hr + " "
        if len(hours) < 3:
            hours = "<MISSING>"
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
        if not city:
            city = "<MISSING>"
        if city.find(".Rd"):
            city = city.replace("Rd.", "")
        if city.find(".Dr"):
            city = city.replace("Dr.", "")
        if city.find("Ave."):
            city = city.replace("Ave.", "")
        lat = lat.lstrip()
        long = long.lstrip()
        long = long.rstrip()
        phone = phone.lstrip()
        store = store.lstrip()
        street = street.lstrip()
        street = street.replace(",", "")
        city = city.lstrip()
        city = city.replace(",", "")
        state = state.lstrip()
        state = state.replace(",", "")
        pcode = pcode.lstrip()
        pcode = pcode.replace(",", "")

        phone1 = list(phone)

        if phone1[3] == " ":
            phone1[3] = "-"
        phone = ""
        for ele in phone1:
            phone += ele
        phone = phone.split(" ", 1)[0]

        if phone == "440-96-PERCH440-967-3724\t\t\t\t\t\t\t\t":
            phone = "440-967-3724"
        if "Coming" in phone:
            phone = "<MISSING>"
        data.append(
            [
                "http://thelube.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                lat,
                long,
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
