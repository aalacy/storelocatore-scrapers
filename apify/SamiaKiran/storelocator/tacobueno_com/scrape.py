import csv
import sgzip
import re
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tacobueno_com")
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
    # Your scraper here
    data = []
    titlelist = []
    MAX_RESULTS = 15  # max number of results the website gives
    MAX_DISTANCE = 50.0  # max number of distance from the zip it covers
    pattern = re.compile(r"\s\s+")
    search = (
        sgzip.ClosestNSearch()
    )  # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    query_coord = search.next_zip()
    while query_coord:
        count = 0
        result_coords = []
        url = "https://www.tacobueno.com/locations/&zip=" + query_coord
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
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
                if title in titlelist:
                    pass
                else:
                    titlelist.append(title)
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
        except Exception as e:
            logger.info(e)
            input()
        ##            pass

        search.max_distance_update(MAX_DISTANCE)
        """elif count == MAX_RESULTS:  # check to save lat lngs to find zip that excludes them
            logger.info("max count update")"""
        search.max_count_update(result_coords)
        query_coord = search.next_zip()
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
