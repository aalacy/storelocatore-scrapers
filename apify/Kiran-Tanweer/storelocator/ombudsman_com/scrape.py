from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser


logger = SgLogSetup().get_logger("ombudsman_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        temp_list = []
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
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    all_stores = []
    all_coords = []
    search_url = "https://www.ombudsman.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    statelist = soup.find("ul", {"id": "state-list"}).findAll("a")
    for state in statelist:
        link = state["href"]
        stores_req = session.get(link, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        coords = soup.find("script", {"id": "mappress-js-after"})
        coords = str(coords)
        coords = coords.split('"point":{')
        for i in coords:
            if i.find("lat") != -1:
                i = i.split("},")[0]
                all_coords.append(i)
    for state in statelist:
        link = state["href"]
        stores_req = session.get(link, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        content = soup.findAll("div", {"class": "location-group clearfix"})
        for locs in content:
            locs = locs.findAll("ul")
            for loc in locs:
                center = str(loc)
                if center.find("<li") != -1:
                    center = loc.findAll("li")
                    for store in center:
                        all_stores.append(store)
                else:
                    all_stores.append(loc)
    for store, coords in zip(all_stores, all_coords):
        title = store.find("h4").text
        address = store.find("p").text.strip()
        parsed = parser.parse_address_usa(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"
        phone = store.text
        if phone.find("(") != -1:
            phone = phone.split(pcode)[1].strip()
        else:
            phone = "<MISSING>"
        lat, lng = coords.split(",")
        lat = lat.split('"lat":"')[1].split('"')[0].strip()
        lng = lng.split('"lng":"')[1].split('"')[0].strip()
        if lat == "":
            lat = "<MISSING>"
        if lng == "":
            lng = "<MISSING>"
        link = "https://www.ombudsman.com/state/" + state.lower()

        if title == "Cartersville":
            street = "134 Market Sq Shopping Center"
            city = "Cartersville"
        data.append(
            [
                "https://www.ombudsman.com/",
                link,
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
                "<MISSING>",
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
