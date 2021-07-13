import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
import time
from sgscrape import sgpostal as parser

logger = SgLogSetup().get_logger("comfortdental_com")

session = SgRequests()


def write_output(store):
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
        for row in store:
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
    store = []
    base_url = "https://comfortdental.com"
    url = "https://comfortdental.com/wp-admin/admin-ajax.php"

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,pt;q=0.8",
        "content-length": "206",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://comfortdental.com",
        "referer": "https://comfortdental.com/find-a-dentist/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    locatornonce = session.post(
        url, headers=headers, data="action=locatornonce"
    ).json()["nonce"]
    payload = (
        "action=locate&address=80261&formatted_address=Denver%2C+CO+80261%2C+USA&locatorNonce="
        + str(locatornonce)
        + "&distance=10000000000&latitude=39.73999999999999&longitude=-104.98&unit=miles&geolocation=false&allow_empty_address=false"
    )
    json_data = session.post(url, headers=headers, data=payload).json()

    for data in json_data["results"]:
        location_name = data["title"]
        if "closed" in location_name.lower():
            continue
        store_number = data["id"]
        lat = data["latitude"]
        lng = data["longitude"]
        page_url = data["permalink"]
        soup = list(BeautifulSoup(data["output"], "html.parser").stripped_strings)
        street = soup[-5]
        locality = soup[-4]
        address = street + " " + locality
        phone = soup[-3]

        if phone == "New Braunfels, TX 78130":
            phone = "<MISSING>"
            street = soup[-4]
            locality = soup[-3]
            address = street + " " + locality

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

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
        }
        location_soup = BeautifulSoup(
            session.get(page_url, headers=headers).content, "html.parser"
        )
        try:
            hours = " ".join(list(location_soup.find(id="hoursTable").stripped_strings))
            if "Coming Soon" in hours:
                continue
        except:
            hours = "<MISSING>"

        phone = phone.rstrip("â€¬")

        store.append(
            [
                base_url,
                page_url,
                location_name,
                street,
                city,
                state,
                pcode,
                "US",
                store_number,
                phone,
                "<MISSING>",
                lat,
                lng,
                hours,
            ]
        )
    return store


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    store = fetch_data()
    write_output(store)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
