from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress

logger = SgLogSetup().get_logger("lottoil_com")

session = SgRequests()

headers = {
    "authority": "lottoil.com",
    "method": "GET",
    "path": "/convenience-store-locations/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "identity",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "_gid=GA1.2.1335869901.1612637934; mrsrc=direct; _gat_UA-119706762-60=1; _ga_11111ABCDE=GS1.1.1612676633.2.1.1612676653.0; _ga=GA1.2.1896903548.1612637934",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
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
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    url = "https://lottoil.com/convenience-store-locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    info = soup.find("section", {"class": "locations"}).findAll(
        "div", {"class": "location"}
    )
    for loc in info:
        title = loc.find("h3").text
        storeid = title.split("#")[-1]
        address = loc.findAll("div", {"class": "address"})
        phone = address[1].text.strip()
        phone = phone.lstrip("Phone:").strip()
        address = address[0].find("a")["href"]
        address = address.split("/")[-1]
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
        street = street.lstrip()
        street = street.replace(",", "")
        city = city.lstrip()
        city = city.replace(",", "")
        state = state.lstrip()
        state = state.replace(",", "")
        pcode = pcode.lstrip()
        pcode = pcode.replace(",", "")

        coords = soup.find("script", {"id": "custom-map-js-extra"})
        coords = str(coords)
        coords = coords.split(title)[1].split("}")[0]
        lat = coords.split('"lat":')[1].split(",")[0]
        lng = coords.split('"lng":')[1].strip()

        data.append(
            [
                "https://lottoil.com/",
                "https://lottoil.com/convenience-store-locations/",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                storeid,
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
