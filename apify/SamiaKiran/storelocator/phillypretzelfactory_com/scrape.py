import csv
import usaddress
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup


website = "phillypretzelfactory_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "phillypretzelfactory.com",
    "method": "GET",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "SSESS0f74228a2790db1ff054f928dc1cc17e=8962f0cfab311a36f3fddc8ec6328d7d; _ga=GA1.2.842911136.1608100167; _fbp=fb.1.1608100170613.1636246446; SESS0f74228a2790db1ff054f928dc1cc17e=c11e3f2a1dfb1723593db555f1be197a; _gid=GA1.2.1177492152.1608820608; _gat=1",
    "referer": "https: //phillypretzelfactory.com/store-locator/",
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
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
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
    if True:
        for st in states:
            coordinates = (
                "https://maps.googleapis.com/maps/api/geocode/json?address=%27"
                + st
                + "+%27&key=AIzaSyCT4uvUVAv4U6-Lgeg94CIuxUg-iM2aA4s&components=country%3AUS%27"
            )
            address_list = session.get(
                coordinates, headers=headers, verify=False
            ).json()["results"]

            for address in address_list:
                LA = str(round(address["geometry"]["location"]["lat"], 7))
                LO = str(round(address["geometry"]["location"]["lng"], 7))
            url = (
                "https://phillypretzelfactory.com/wp-content/themes/philly-pretzel-factory/ajax/storelocator.php?lat="
                + LA
                + "&lng="
                + LO
                + "&radius=200&onlineOrder=false"
            )
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.find("markers").findAll("marker")
            for loc in loclist:
                title = loc["name"]
                store = loc["id"]
                phone = loc["phone"]
                if not phone:
                    phone = "<MISSING>"
                lat = loc["lat"]
                longt = loc["lng"]
                try:
                    hours = loc["allhours"]
                    hours = hours.replace("<br />", "  ")
                except:
                    hours = "<MISSING>"
                address = loc["address"]
                templink = loc["slug"]
                link = "https://phillypretzelfactory.com/locations/" + templink + "/"
                if not address:
                    street = "<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    pcode = "<MISSING>"
                address = address.replace(",", " ")
                if "USA" in address:
                    address = address.replace("USA", "")
                if "***" in address:
                    address = address.split("***", 1)[0]
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
                if "Virginia Beach" in street:
                    temp_list = street.split("Virginia Beach", 1)
                    city = "Virginia Beach"
                    street = temp_list[0]
                    state = temp_list[1]
                if "Neptune New" in city:
                    city = city.split()
                    tempstate = city[1]
                    city = city[0]
                    state = tempstate + state
                    state = state.strip()
                if not pcode:
                    pcode = "<MISSING>"
                if not city:
                    city = "<MISSING>"
                if not state:
                    state = "<MISSING>"
                if not street:
                    street = "<MISSING>"
                data.append(
                    [
                        "https://phillypretzelfactory.com/",
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
        return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
