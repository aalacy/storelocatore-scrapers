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
    url = "https://sugarfishsushi.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "row clearfix"})[2].findAll("a")
    lhour = soup.findAll("div", {"class": "opening-block"})[0].text
    nhour = soup.findAll("div", {"class": "opening-block"})[2].text
    p = 0
    for div in divlist:
        link = div["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.findAll("h1")[1].text
        address = soup.find("h6").text
        if "Add Me to Seating WaitList" in address:
            address = soup.findAll("h5", {"class": "entry-sub-title"})[1].text
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
        try:
            maplink = soup.find("h6").find("a")["href"]
            r = session.get(maplink, headers=headers, verify=False)
            lat, longt = r.url.split("@", 1)[1].split("data", 1)[0].split(",", 1)
            longt = longt.split(",", 1)[0]
        except:
            lat = longt = "<MISSING>"
        if "NY" in state:
            hours = nhour
        else:
            hours = lhour
        try:
            hours = hours.split("MON", 1)[1].replace("\t", " ").replace("\n", " ")
            hours = "MON " + hours
        except:
            pass
        try:
            hours = hours.split("Mon", 1)[1].replace("\t", " ").replace("\n", " ")
            hours = "Mon " + hours
        except:
            pass
        phone = soup.find("h3").text
        data.append(
            [
                "https://sugarfishsushi.com/",
                link,
                title.replace("\n", "").replace("\t", "").strip(),
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone.replace("\n", "")
                .replace("\t", "")
                .replace("\u202c", "")
                .replace("\u202d", "")
                .strip(),
                "<MISSING>",
                lat,
                longt,
                hours.replace("\n", " ")
                .replace(":00", ":00 ")
                .replace("\xa0", " ")
                .replace("ight", "ight ")
                .strip(),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
