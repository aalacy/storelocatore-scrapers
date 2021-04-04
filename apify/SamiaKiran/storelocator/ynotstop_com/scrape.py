import csv
import usaddress
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "ynotstop_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    final_data = []
    if True:
        url = "http://www.ynotstop.com/stores"
        r = session.get(url, headers=headers)
        coords = (
            r.text.split(
                "var companyMarker = new Array();",
            )[1]
            .split("var contentString = ", 1)[0]
            .strip()
        )
        coords = coords.replace("\n", "").replace("\t", "").replace('"', "")
        coords = coords.split("new google.maps.Marker({")
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "StoreWrap"})
        for loc in loclist:
            store = loc["id"].replace("BackToLocation", "")
            temp = loc.find("div", {"class": "DetailWrap"})
            title = temp.find("h3").text
            address = temp.find("h4").text
            temp_check = loc.find("div", {"class": "EditorText"}).text
            if "Coming Soon!" in temp_check:
                phone = "<MISSING>"
                hours = "<MISSING>"
            else:
                phone = temp.find("div", {"class": "PhoneTag"})
                phone = phone.find("h2").text
                try:
                    hours = loc.find("li").text.split("|")[0]
                except:
                    hours = "<MISSING>"
            title = title.replace("'", "\\'")
            for temp_coords in coords:
                if title in temp_coords:
                    temp_coords = temp_coords.split("LatLng(")[1].split("),", 1)[0]
                    temp_coords = temp_coords.split(",")
                    lat = temp_coords[0]
                    longt = temp_coords[1]
            address = address.replace(",", " ")
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
            final_data.append(
                [
                    "http://www.ynotstop.com/",
                    "http://www.ynotstop.com/stores",
                    title.strip(),
                    street.strip(),
                    city.strip(),
                    state.strip(),
                    pcode.strip(),
                    "USA",
                    store.strip(),
                    phone.strip(),
                    "<MISSING>",
                    lat.strip(),
                    longt.strip(),
                    hours.strip(),
                ]
            )
        return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
