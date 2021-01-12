import csv
import usaddress
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list

website = "tacobueno_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
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
        # Body
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    data = []
    zips = static_zipcode_list(radius=50, country_code=SearchableCountries.USA)
    if True:
        for zip_code in zips:
            search_url = "https://www.tacobueno.com/locations/&zip=" + zip_code
            stores_req = session.get(search_url, headers=headers)
            soup = BeautifulSoup(stores_req.text, "html.parser")
            loclist = soup.findAll("div", {"class": "map-listing_item active"})
            for loc in loclist:
                title = loc.find("h2").text
                store = title.split("-", 1)[1].strip()
                if "temporarily closed" in store:
                    store = store.split("(", 1)[0]
                    store = store.strip()
                address = loc.find("address").text
                temp = title.replace("-", "")
                temp = " ".join(temp.split())
                temp = "Call" + " " + temp
                phone = loc.find("a").text
                if not phone:
                    phone = "<MISSING>"
                gps = loc.get("data-gps").split(",")
                lat = gps[0]
                longt = gps[1]
                hour_list = loc.find("ul").findAll(
                    "li", {"class": "list-toggle-item inactive"}
                )
                hours = ""
                for hour in hour_list:
                    hours = hours + " " + hour.text
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
                data.append(
                    [
                        "https://www.tacobueno.com/",
                        "https://www.tacobueno.com/locations/",
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
        return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
