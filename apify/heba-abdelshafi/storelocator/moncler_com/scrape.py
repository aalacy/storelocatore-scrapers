from bs4 import BeautifulSoup
import csv
import time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("moncler_com")

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
    data = []
    p = 0
    url = "https://www.moncler.com/en-us/storeslocator"
    r = session.get(url, headers=headers, verify=False)

    soup = BeautifulSoup(r.text, "html.parser")

    country_list = soup.findAll("a", {"class": "Directory-listLink"})

    for country in country_list:
        if (
            country["href"].find("storeslocator/canada") > -1
            or country["href"].find("storeslocator/united-states") > -1
            or country["href"].find("storeslocator/united-kingdom") > -1
        ):
            cclink = "https://www.moncler.com" + country["href"].split("..")[1]
            ccode = "US"
            if country["href"].find("storeslocator/canada") > -1:
                ccode = "CA"
            elif country["href"].find("storeslocator/united-kingdom") > -1:
                ccode = "GB"
            r = session.get(cclink, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            maindiv = soup.find("ul", {"class": "Directory-listLinks"})
            citylist = maindiv.findAll("li", {"class": "Directory-listItem"})

            for city in citylist:

                clink = (
                    "https://www.moncler.com/en-us"
                    + city.find("a")["href"].split("../en-us")[1]
                )

                count = city.find("a")["data-count"].replace(")", "").replace("(", "")
                count = (int)(count)

                r1 = session.get(clink, headers=headers, verify=False)
                soup = BeautifulSoup(r1.text, "html.parser")
                branchlink = soup.findAll("a", {"class": "Teaser-titleLink"})
                flag = 0
                if count == 1:
                    branchlink = []
                    branchlink.append(clink)
                    flag = 1

                for branch in branchlink:

                    if flag == 0:
                        link = (
                            "https://www.moncler.com/en-us"
                            + branch["href"].split("../en-us")[1]
                        )

                        r = session.get(link, headers=headers, verify=False)
                        soup = BeautifulSoup(r.text, "html.parser")

                    else:
                        soup = BeautifulSoup(r1.text, "html.parser")
                        link = clink

                    title = soup.find("h1").text
                    street = soup.find(
                        "span", {"class": "c-address-street-1"}
                    ).text.replace("\n", " ")
                    try:
                        street += ", " + soup.find(
                            "span", {"class": "c-address-street-2"}
                        ).text.replace("\n", " ")
                    except:
                        pass
                    city = soup.find("span", {"class": "c-address-city"}).text
                    if ccode != "GB":
                        state = soup.find("abbr", {"itemprop": "addressRegion"}).text
                    else:
                        state = "<MISSING>"
                    pcode = soup.find("span", {"class": "c-address-postal-code"}).text
                    try:
                        phone = soup.find("div", {"id": "phone-main"}).text
                    except:
                        phone = "<MISSING>"
                    try:
                        hours = soup.find("table", {"class": "c-hours-details"}).text
                        hours = (
                            hours.split("Hours")[1]
                            .replace("Monday", "Monday ")
                            .replace("Tuesday", " Tuesday ")
                            .replace("Wednesday", " Wednesday ")
                            .replace("Thursday", " Thursday ")
                            .replace("Friday", " Friday ")
                            .replace("Saturday", " Saturday ")
                            .replace("Sunday", " Sunday ")
                        )
                    except:
                        hours = "<MISSING>"
                    lat = soup.find("meta", {"itemprop": "latitude"})["content"]
                    longt = soup.find("meta", {"itemprop": "longitude"})["content"]
                    data.append(
                        [
                            "https://www.moncler.com/",
                            link,
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            ccode,
                            "<MISSING>",
                            phone,
                            "<MISSING>",
                            lat,
                            longt,
                            hours,
                        ]
                    )

                    p += 1

    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
