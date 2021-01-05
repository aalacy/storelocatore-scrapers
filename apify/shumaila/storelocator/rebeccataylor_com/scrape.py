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
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.rebeccataylor.com/store-locator.html"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    store_list = soup.findAll("div", {"class": "store"})
    p = 0
    for store in store_list:
        if "ot" in store["class"]:
            ltype = "Outlet"
        else:
            ltype = "Store"
        title = store.find("h2").text
        det = store.find("p")
        det = re.sub(cleanr, " ", str(det))
        address, hours = det.split("Store Hours:")
        lat = longt = "<MISSING>"
        try:
            lat, longt = (
                store.find("a")["href"].split("@")[1].split("data", 1)[0].split(",", 1)
            )
            longt = longt.split(",", 1)[0]
        except:
            pass
        hours, phone = hours.split("Telephone: ")
        phone = phone.split("Map")[0]
        address = address.replace("\n", "").strip()
        hours = hours.replace("Store Hours:", "").lstrip().replace("\n", "")
        phone = (
            phone.replace("\n", "").lstrip().replace("pm", " pm").replace("am", " am")
        )
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
        data.append(
            [
                "https://www.rebeccataylor.com/",
                "https://www.rebeccataylor.com/store-locator.html",
                title,
                street,
                city.lstrip().replace(",", ""),
                state.lstrip(),
                pcode.lstrip().replace(".", ""),
                "US",
                "<MISSING>",
                phone.rstrip(),
                ltype,
                lat,
                longt,
                hours.rstrip(),
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
