from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser


logger = SgLogSetup().get_logger("dentalservice_net")

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
    locations = []
    search_url = "https://locations.dentalservice.net/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    ##    print(soup)
    children = soup.findAll("li", {"class": "location-link"})
    for child in children:
        ##        print(child)
        links = child.findAll("a")
        for link in links:
            url = link["href"]
            if url.find("locations.") != -1:
                locations.append(url)
                if url.find("/college-station") != -1:
                    locations.pop(-1)
                elif url.find("/cypress-dentures") != -1:
                    locations.pop(-1)
                elif url.find("/denison") != -1:
                    locations.pop(-1)
                elif url.find("/euless") != -1:
                    locations.pop(-1)
                elif url.find("/georgetown") != -1:
                    locations.pop(-1)
                elif url.find("/granbury") != -1:
                    locations.pop(-1)
                elif url.find("/greenville") != -1:
                    locations.pop(-1)
                elif url.find("/humble") != -1:
                    locations.pop(-1)
                elif url.find("/kyle") != -1:
                    locations.pop(-1)
                elif url.find("/lake-worth") != -1:
                    locations.pop(-1)
                elif url.find("/pearland") != -1:
                    locations.pop(-1)
                elif url.find("/schertz") != -1:
                    locations.pop(-1)
                elif url.find("/waxahachie") != -1:
                    locations.pop(-1)
    for loc in locations:
        stores_req = session.get(loc, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        info = soup.find("div", {"class": "service-info"})
        title = info.find("h1").text
        address = info.find("h3").text
        hours = info.find("h4", {"id": "hours"})
        mon = "Monday - " + hours.find("span", {"class": "day Monday"}).text
        tue = "Tuesday - " + hours.find("span", {"class": "day Tuesday"}).text
        wed = "Wednesday - " + hours.find("span", {"class": "day Wednesday"}).text
        thu = "Thursday - " + hours.find("span", {"class": "day Thursday"}).text
        fri = "Friday - " + hours.find("span", {"class": "day Friday"}).text
        sat = "Saturday" + hours.find("span", {"class": "day Saturday"}).text
        sun = "Sunday" + hours.find("span", {"class": "day Sunday"}).text
        hoo = (
            mon + " " + tue + " " + wed + " " + thu + " " + fri + " " + sat + " " + sun
        )
        phone = info.findAll("button")[-1].find("a")["href"]
        phone = phone.replace("tel:", "").strip()
        script = soup.find("script", {"type": "application/ld+json"})
        script = str(script)
        lat = script.split('"latitude":')[1].split(",")[0]
        lng = script.split('"longitude":')[1].split(",")[0]
        lng = lng.split("}")[0]
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

        data.append(
            [
                "https://www.dentalservice.net/",
                loc,
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
                hoo,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
