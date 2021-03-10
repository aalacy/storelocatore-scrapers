from bs4 import BeautifulSoup
import csv
import json
import time
import re
from sgselenium import SgChrome
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tacocabana_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    final_data = []
    with SgChrome() as driver:
        driver.get("https://www.tacocabana.com/locations")
        time.sleep(25)
        driver.find_element_by_xpath(
            "//button[contains(., 'view all locations')]"
        ).click()
        time.sleep(40)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        loclist = soup.findAll(
            "div", {"class": "card-info styles__StyledCardInfo-s1y7dfjk-3 gCNPSz"}
        )
    r = session.get("https://www.tacocabana.com/locations", headers=headers)
    temp_r = r.text.split(',"list":')[1].split(',"detail"', 1)[0]
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    for loc in loclist:
        title = loc.find("h3")
        title = title.find("a").text
        store = title.split("#", 1)[1]
        address = loc.find("p")
        address = re.sub(cleanr, "\n", str(address))
        address = re.sub(pattern, "\n", address)
        content = address.splitlines()
        if len(content) == 7:
            street = " ".join(content[1:3])
            street = street.replace("&amp;", "&")
            city = content[3]
            state = content[4]
            pcode = content[5]
            phone = content[6]
        elif len(content) == 4:
            street = content[1]
            street = street.replace("&amp;", "&")
            temp = content[2].split()
            if len(temp) == 4:
                city = " ".join(temp[0:2])
                state = temp[2]
                pcode = temp[3]
            else:
                city = temp[0]
                state = temp[1]
                pcode = temp[2]
            phone = content[3]
        elif len(content) == 5:
            try:
                street = content[2]
                street = street.replace("&amp;", "&")
                temp = content[3].split()
                city = temp[0]
                state = temp[1]
                pcode = temp[2]
                phone = content[4]
            except:
                street = content[1]
                street = street.replace("&amp;", "&")
                city = content[2]
                temp = content[3].split()
                state = temp[0]
                pcode = temp[1]
                phone = content[4]
        else:
            street = content[1]
            street = street.replace("&amp;", "&")
            city = content[2]
            state = content[3]
            pcode = content[4]
            phone = content[5]
        try:
            hours = loc.text.split(")", 1)[1]
            hours = hours.split("O", 1)[1]
            hours = "O" + hours
        except:
            hours = "<MISSING>"
        temp_list = json.loads(temp_r)
        lat = "<MISSING>"
        longt = "<MISSING>"
        for temp in temp_list:
            if temp["brand_id"] == store:
                lat = temp["latitude"]
                longt = temp["longitude"]
        final_data.append(
            [
                "https://www.tacocabana.com/",
                "https://www.tacocabana.com/locations",
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
    return final_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
