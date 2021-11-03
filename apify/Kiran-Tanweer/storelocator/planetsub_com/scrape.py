from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress

logger = SgLogSetup().get_logger("planetsub_com")

session = SgRequests()

headers = {
    "authority": "planetsub.com",
    "method": "POST",
    "path": "/contact/find-a-location/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "identity",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "content-length": "14",
    "content-type": "application/x-www-form-urlencoded",
    "cookie": "PHPSESSID=lnpc04bv70tij3suieb2ngo1o0; __utmc=230204893; __utmz=230204893.1611633760.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _fbp=fb.1.1611633760304.649577070; __utma=230204893.1389812213.1611633760.1611775008.1611806536.3; __utmt=1; __utmb=230204893.2.10.1611806536",
    "origin": "https://planetsub.com",
    "referer": "https://planetsub.com/contact/find-a-location/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
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
    lat = []
    lng = []
    form_data = {"location": "85713"}
    url = "https://planetsub.com/contact/find-a-location/"
    r = session.post(url, headers=headers, data=form_data, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    locations = soup.find("div", {"id": "mapContainer"})
    loc = locations.findAll("div", {"class": "popup"})

    locations = str(locations)
    info = locations.split("var locations = ")[1].split(
        "locations = JSON.parse(locations);"
    )[0]
    coords = info.split("],[")
    j = 0
    for c in range(1, 34):
        index = '",' + str(c) + ',"'
        centre = coords[c - 1].split(index)[0]
        centre = centre.split('","')
        lat.append(centre[1])
        lng.append(centre[2])
    for l in loc:
        title = l.find("span", {"class": "franchise_title_name"}).text.strip()
        address = l.find("span", {"class": "franchise_address"}).text.strip()
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

        hours = l.find("span", {"class": "franchise_hours"}).text.strip()
        hours = hours.replace("\n", " ")
        hours = hours.rstrip(" NOW OPEN")
        phone = l.find("span", {"class": "franchise_phone"}).text.strip()
        phone = phone.lstrip("Phone: ").strip()
        latitude = lat[j].strip()
        longitude = lng[j].strip()

        data.append(
            [
                "https://planetsub.com/",
                "https://planetsub.com/contact/find-a-location/",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                latitude,
                longitude,
                hours,
            ]
        )

        j = j + 1
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
