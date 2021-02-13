from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
from datetime import datetime as dt


logger = SgLogSetup().get_logger("eddiev_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    url = "https://www.eddiev.com/locations/all-locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    storelist = soup.find("div", {"class": "cols"})
    more_link = storelist.findAll("div", {"class", "more_links"})
    for link_div in more_link:
        link = link_div.find("a", {"id": "locDetailsId"})["href"]
        link = "https://www.eddiev.com" + link
        p = session.get(link, headers=headers, verify=False)
        bs = BeautifulSoup(p.text, "html.parser")
        left_bar = bs.find("div", {"class": "left-bar"})
        title = left_bar.find("h1", {"class": "style_h1"}).text.strip()
        addr_div = left_bar.find("p")
        addr_div = str(addr_div)
        addr_div = addr_div.strip()
        info = addr_div.split("\n")
        street = info[2]
        street = street.rstrip("<br/>")
        city = info[4]
        city = city.rstrip(",")
        state = info[5].strip()
        pcode = info[6]
        pcode = pcode.rstrip("<br/>")
        phone = info[7]
        phone = phone.rstrip("</p>")
        hours = left_bar.findAll("ul", {"class": "inline top-bar"})
        hrs = ""
        for hr in hours:
            days = hr.findAll("li")
            day = days[0].text.strip()
            time = days[1].text.strip()
            now = dt.today()
            now = now.strftime("%a %b %d")
            time = time.replace(now, "").strip()
            time = time.replace(":00 EST 2021", "").strip()
            hoo = day + " " + time
            hoo = hoo.replace("Today (", "")
            hoo = hoo.replace(")", "").strip()
            hrs = hrs + " " + hoo
        hrs = hrs.strip()
        script = bs.find("script", {"type": "application/ld+json"})
        script = str(script)
        lat = script.split('"latitude":"')[1].split('"')[0]
        lng = script.split('"longitude":"')[1].split('"')[0]
        storeid = link.split("/")[-1]

        data.append(
            [
                "https://www.eddiev.com/",
                link,
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
                hrs,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
