from bs4 import BeautifulSoup
import csv
import re
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("241pizza_com")

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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.241pizza.com/locations.aspx"
    req = session.get(url, headers=headers)
    soup = BeautifulSoup(req.text, "html.parser")
    cities = soup.find("select", {"id": "city"}).findAll("option")
    for city in cities:
        if city["value"] != "":
            city = city["value"]
            form_data = {
                "city": city,
                "address": "",
            }
            r = session.post(url, headers=headers, data=form_data)
            soup = BeautifulSoup(r.text, "html.parser")
            loc_box = soup.findAll("div", {"class": "addr-box"})
            for loc in loc_box:
                link = loc.find("a", {"class": "locationname"})["href"]
                storeid = link.split("-")[-1]
                street = loc.find("p", {"class": "fontXXL"}).text.strip()
                locality = (
                    loc.find("p", {"class": "fontpro under-line Locationswidth qq"})
                    .find("span")
                    .text.strip()
                )
                locality = locality.split(",")
                city = locality[0]
                state = locality[1]
                pcode = locality[-1]
                phone = loc.find("a", {"class": "pull-right"}).text.strip()
                coords = loc.find("div", {"class": "storeDetails"}).find("a")["href"]
                coords = (
                    coords.split("EndAddress=")[1].split("&Storenumber")[0].split(",")
                )
                lat = coords[0]
                lng = coords[1]
                link = "https://www.241pizza.com/" + link
                p = session.get(link, headers=headers)
                soup = BeautifulSoup(p.text, "html.parser")
                title = soup.find("article", {"class": "col-lg-5 col-md-6"})
                if title is None:
                    title = "<MISSING>"
                else:
                    title = title.find("h1").text
                section = soup.find("main", {"id": "main"})
                if section is None:
                    hours = "<MISSING>"
                else:
                    section = section.find(
                        "aside", {"class": "col-lg-4 col-md-3"}
                    ).find("div")
                    if section is None:
                        hours = "<MISSING>"
                    else:
                        section = section.text
                        hours = section.replace("\n", " ").strip()
                        hours = re.sub(pattern, " ", hours)
                        hours = re.sub(cleanr, " ", hours)
                link = link.strip()
                title = title.strip()
                street = street.strip()
                city = city.strip()
                state = state.strip()
                pcode = pcode.strip()
                storeid = storeid.strip()
                phone = phone.strip()
                lat = lat.strip()
                lng = lng.strip()
                hours = hours.strip()

                data.append(
                    [
                        "https://www.241pizza.com/",
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        "CA",
                        storeid,
                        phone,
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
