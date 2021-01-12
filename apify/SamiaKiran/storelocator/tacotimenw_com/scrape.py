import csv
import usaddress
import json
from sgrequests import SgRequests
from sglogging import sglog


website = "tacotimenw_com"
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
    data = []
    url = "https://tacotimenw.com/find-us/"
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split("dataRaw:")[1].split("dataType:", 1)[0]
    loclist = loclist.replace("}]}],", "}]}]").replace("\n", "")
    loclist = json.loads(loclist)
    for loc in loclist:
        title = loc["name"]
        if "&#8211;" in title:
            title = title.replace("&#8211;", " - ")
        if "&#038;" in title:
            title = title.replace("&#038;", " - ")
        store = loc["id"]
        lat = loc["lat"]
        longt = loc["lng"]
        ccode = loc["country"]
        phone = loc["phone"]
        hours = ""
        open_time = loc["open"]
        close_time = loc["close"]
        hours = open_time + " " + close_time
        hours = hours.strip()
        if not hours:
            hourlist = []
            templist = loc["wh"]
            for temp in templist:
                if "Dining" in temp["desc"]:
                    hourlist.append(temp)
            if not hourlist:
                hourlist = templist.copy()
            for hour in hourlist:
                open_time = hour["open_time"]
                close_time = hour["close_time"]
                hours = hours + hour["desc"] + " " + open_time + " " + close_time + " "
            if "Lobby" in hours:
                hours = hours.split("Lobby", 1)[1]
                hours = "Lobby" + hours
        if not hours:
            hours = "<MISSING>"
        address = loc["address"]
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
        city = city.strip()
        state = state.strip()
        street = street.strip()
        if not pcode:
            pcode = "<MISSING>"
        if "USA" in state:
            state = state.split("USA", 1)[0]
        data.append(
            [
                "https://tacotimenw.com/",
                "https://tacotimenw.com/find-us/",
                title,
                street,
                city,
                state,
                pcode,
                ccode,
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
    data = fetch_data()
    write_output(data)


scrape()
