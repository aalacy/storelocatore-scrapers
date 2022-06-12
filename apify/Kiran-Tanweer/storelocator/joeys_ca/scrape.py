from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("joeys_ca")

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
    url = "https://joeys.ca/locations"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    state_list = soup.find("div", {"id": "location-list"}).findAll("a")
    for state in state_list:
        state_link = "https://joeys.ca" + state["href"]
        r = session.get(state_link, headers=headers)
        bs = BeautifulSoup(r.text, "html.parser")
        loc_list = bs.find("div", {"id": "location-list"}).findAll("tbody")
        for loc_body in loc_list:
            loc_link = loc_body.findAll("a")
            for atag in loc_link:
                link = atag["href"]
                if link.find("/") != -1:
                    loc_url = "https://joeys.ca" + link
                    p = session.get(loc_url, headers=headers)
                    bs2 = BeautifulSoup(p.text, "html.parser")
                    locdiv = bs2.find("div", {"class": "container primary"})
                    title = locdiv.find("div", {"id": "title-bar"}).find("h1").text
                    lat = locdiv.find("meta", {"itemprop": "latitude"})["content"]
                    lng = locdiv.find("meta", {"itemprop": "longitude"})["content"]
                    street = locdiv.find("span", {"itemprop": "streetAddress"}).text
                    city = locdiv.find("span", {"itemprop": "addressLocality"}).text
                    state = locdiv.find("span", {"itemprop": "addressRegion"}).text
                    pcode = locdiv.find("span", {"itemprop": "postalCode"}).text
                    phone = locdiv.find("span", {"itemprop": "telephone"}).text
                    hours = locdiv.find("div", {"class": "content"}).findAll("p")[-1]
                    hours = hours.findAll("time")
                    hoo = ""
                    if len(hours) == 0:
                        hoo = "<MISSING>"
                    else:
                        for hr in hours:
                            hoo = hoo + " " + hr.text
                    hoo = hoo.strip()

                    data.append(
                        [
                            "https://joeys.ca/",
                            loc_url,
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            "CAN",
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
