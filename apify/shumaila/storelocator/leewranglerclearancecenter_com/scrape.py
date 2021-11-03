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
    url = "https://leewranglerclearancecenter.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "address-box"})
    p = 0
    for div in divlist:
        title = (
            div.find("h3").text + " - " + div.find("p", {"class": "store_name"}).text
        )
        ltype = div.find("div", {"class": "store_logo"}).find("img")["src"]
        if "logo-one" in ltype:
            ltype = "Outlet"
        elif "logo-two" in ltype:
            ltype = "Clearance Center"
        address = div.findAll("p")[1].text.replace(",", "").replace("USA ", "")
        try:
            phone = div.select_one("a[href*=tel]").text.replace("\n", "").strip()
        except:
            phone = "<MISSING>"
        hours = (
            div.findAll("p")[-1]
            .text.replace("Modified Hours:", "")
            .replace("\n", " ")
            .replace("\r", "")
            .strip()
        )
        address = address.replace(phone, "")
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
        street = street.lstrip().replace(",", "")
        city = city.lstrip().replace(",", "")
        state = state.lstrip().replace(",", "")
        pcode = pcode.lstrip().replace(",", "")
        try:
            pcode = pcode.lstrip().split(" ", 1)[0]
        except:
            pass
        if len(pcode) < 3:
            pcode = "<MISSING>"
        data.append(
            [
                "https://leewranglerclearancecenter.com/",
                url,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                ltype,
                "<MISSING>",
                "<MISSING>",
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
