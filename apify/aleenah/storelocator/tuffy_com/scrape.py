from bs4 import BeautifulSoup
import csv
import re
import usaddress

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
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
    pattern = re.compile(r"\s\s+")
    data = []
    titlelist = []
    p = 0
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "ME",
        "MD",
        "MI",
        "MN",
        "MS",
        "MO",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "PA",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WV",
        "WI",
    ]
    for statenow in states:
        coordlist = []
        url = "https://www.tuffy.com/location_search?zip_code=" + statenow
        if statenow == "ID":
            url = "https://www.tuffy.com/location_search?zip_code=ID&location_destination=/&lat_lng=(44.0682019,%20-114.7420408)"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll("div", {"class": "contact-info"})

        if len(divlist) == 0:
            continue
        latlnglist = r.text.split("var locations = [", 1)[1].split("];", 1)[0]
        while True:
            try:
                temp, latlnglist = latlnglist.split("(", 1)[1].split("),", 1)
                coordlist.append(temp)
            except:
                break

        for j in range(0, len(divlist)):
            div = divlist[j]
            title = div.find("h2").text.strip().split("T", 1)[1]
            title = "T" + title

            address = div.find("address").text
            address = re.sub(pattern, " ", address).strip()

            try:
                address = address.split("MANAGER", 1)[0]
            except:
                pass
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
            if street in titlelist:
                continue
            titlelist.append(street)
            city = city.lstrip().replace(",", "")
            state = state.lstrip().replace(",", "")
            pcode = pcode.lstrip().replace(",", "")

            phone = div.find("span", {"class": "tel"}).text
            hours = div.find("div", {"class": "schedule-holder"}).text
            hours = re.sub(pattern, "\n", hours).strip().replace("\n", " ")

            lat, longt = coordlist[j].split(", ")

            data.append(
                [
                    "https://www.tuffy.com/",
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
