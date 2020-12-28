from bs4 import BeautifulSoup
import csv
import usaddress
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
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
    p = 0
    data = []
    titlelist = []
    zips = static_zipcode_list(radius=200, country_code=SearchableCountries.USA)
    for zip_code in zips:
        url = (
            "https://www.sperry.com/en/stores?distanceMax=300&distanceUnit=mi&country=US&zip="
            + zip_code
            + "&formType=findbyzipandcountry&start=0&sz=100"
        )
        obj = {"format": "ajax"}
        r = session.post(url, data=obj, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            divlist = soup.find("table").findAll("tr")
        except:
            continue
        for div in divlist:
            title = div.find("span").text.split(".")[1].replace("\n", "")
            try:
                hours = div.find("div", {"class": "store-hours"}).text
            except:
                hours = div.find("td", {"class": "store-hours"}).text
            store = div.find("a", {"class": "editbutton"})["id"]
            if "Check store inventory" not in hours or store in titlelist:
                continue
            titlelist.append(store)
            hours = (
                hours.replace("Check store inventory", "")
                .replace("\n", " ")
                .replace("pm", "pm ")
                .strip()
            )
            address = (
                div.find("a", {"class": "getdirection"})["href"]
                .split("q=", 1)[1]
                .replace(",", "")
            )
            phone = div.find("td", {"class": "store-phone"}).text
            lat = (
                div.find("a", {"class": "editbutton"})["data-location"]
                .split("'latitude':'", 1)[1]
                .split("'", 1)[0]
            )
            longt = (
                div.find("a", {"class": "editbutton"})["data-location"]
                .split("'longitude':'", 1)[1]
                .split("'", 1)[0]
            )
            link = (
                "https://www.sperry.com"
                + div.find("a", {"class": "editbutton"})["href"]
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
                temp, city = city.split("OUTLETS ", 1)
                street = street + " " + temp + " OUTLETS"
            except:
                pass
            try:
                temp, city = city.split("OUTLET ", 1)
                street = street + " " + temp + " OUTLETS"
            except:
                pass
            try:
                temp, city = city.split("GALLERIA ", 1)
                street = street + " " + temp + " GALLERIA"
            except:
                pass
            try:
                temp, city = city.split("CENTER ", 1)
                street = street + " " + temp + " CENTER"
            except:
                pass
            try:
                temp, city = city.split("PLACE ", 1)
                street = street + " " + temp + " PLACE"
            except:
                pass
            try:
                temp, city = city.split("BEACH ", 1)
                street = street + " " + temp + " BEACH"
            except:
                pass
            try:
                temp, city = city.split("NORTH ", 1)
                street = street + " " + temp + " NORTH"
            except:
                pass
            try:
                temp, city = city.split("ISLAND ", 1)
                street = street + " " + temp + " ISLAND"
            except:
                pass
            try:
                temp = city.split(" ")
                if temp[0] == temp[1] or temp[0] == "null":
                    city = temp[1]
            except:
                pass
            if len(phone) < 3:
                phone = "<MISSING>"
            if len(hours) < 3:
                hours = "<MISSING>"
            data.append(
                [
                    "https://www.sperry.com/",
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
