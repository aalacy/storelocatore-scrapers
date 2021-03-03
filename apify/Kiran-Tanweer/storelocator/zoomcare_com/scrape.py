from bs4 import BeautifulSoup
import csv
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("zoomcare_com")

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
    url = "https://www.zoomcare.com/schedule"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    loc_link = soup.findAll("a", {"class": "modal__location-link w-inline-block"})
    for loc in loc_link:
        link = "https://www.zoomcare.com" + loc["href"]
        req = session.get(link, headers=headers)
        bs = BeautifulSoup(req.text, "html.parser")
        info = bs.find("div", {"class": "location-info__card__content__about__reviews"})
        address = info.find("p").text.strip()
        if address != "":
            title = (
                bs.find("div", {"class": "location-info__card__header"}).find("h3").text
            )
            maps = bs.find("div", {"class": "location-info__card__content__map"}).find(
                "iframe"
            )
            if maps is not None:
                maps = str(maps)
                maps = maps.split("center%3D")[1].split("%26key")[0]
                if maps.find("iframe") != -1:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                else:
                    lat, lng = maps.split("%252C")
            else:
                lat = "<MISSING>"
                lng = "<MISSING>"
            hours = info.find("h5").text.strip()
            hours = hours.replace(" |", ",")
            address = address.strip()
            address = address + " 12345"

            address = address.replace(",", "")
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

            pcode = "<MISSING>"

            data.append(
                [
                    "https://www.zoomcare.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    lat,
                    lng,
                    hours,
                ]
            )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
