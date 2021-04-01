from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ray-ban_com__usa")

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
    url = "https://stores.ray-ban.com/united-states"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loc_block = soup.findAll("li", {"class": "Directory-listTeaser"})
    for loc in loc_block:
        title = loc.find("a", {"class": "Teaser-nameLink"})
        link = title["href"]
        link = "https://stores.ray-ban.com/" + link
        title = title.text
        p = session.get(link, headers=headers)
        soup = BeautifulSoup(p.text, "html.parser")
        street1 = soup.find("span", {"class": "c-address-street-1"}).text
        street2 = soup.find("span", {"class": "c-address-street-2"})
        if street2 is None:
            street = street1
        else:
            street = street1 + " " + street2.text
        city = soup.find("span", {"class": "c-address-city"}).text
        pcode = soup.find("span", {"class": "c-address-postal-code"}).text
        state = soup.find("span", {"class": "c-address-state"})
        if state is None:
            state = "<MISSING>"
        else:
            state = state.text
        phone = soup.find("a", {"class": "Phone-link"}).text
        hours = (
            soup.find("table", {"class": "c-hours-details"}).find("tbody").findAll("tr")
        )
        hoo = ""
        for hr in hours:
            hour = hr.text
            hour = hour.replace("Mon", "Mon ")
            hour = hour.replace("Tue", "Tue ")
            hour = hour.replace("Wed", "Wed ")
            hour = hour.replace("Thu", "Thu ")
            hour = hour.replace("Fri", "Fri ")
            hour = hour.replace("Sat", "Sat ")
            hour = hour.replace("Sun", "Sun ")
            hoo = hoo + ", " + hour
        hoo = hoo.lstrip(", ").strip()
        lat = soup.find("meta", {"itemprop": "latitude"})["content"]
        lng = soup.find("meta", {"itemprop": "longitude"})["content"]

        if (
            hoo
            == "Mon Closed, Tue Closed, Wed Closed, Thu Closed, Fri Closed, Sat Closed, Sun Closed"
        ):
            hoo = "Closed"
        data.append(
            [
                "https://www.ray-ban.com/",
                link,
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
