import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)).get_logger(
    "smashburger_com"
)


def write_output(data):
    with SgWriter() as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():

    all = []

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    }

    res = session.get("https://smashburger.com/locations/", headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    ca = soup.find("div", {"id": "accordion-country-ca"}).find_all(
        "a", {"class": "link-title"}
    )
    us = soup.find("div", {"id": "accordion-country-us"}).find_all(
        "a", {"class": "link-title"}
    )
    dic = {"CA": ca, "US": us}
    for country in dic:
        states = dic[country]
        for state in states:
            url = state.get("href")
            logger.info(url)
            res = session.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            stores = soup.find_all("h3", {"class": "store-title"})

            for store in stores:

                url = store.find("a").get("href")
                logger.info(url)
                res = session.get(url, headers=headers)
                soup = BeautifulSoup(res.text, "html.parser")
                jso = soup.find("script", {"type": "application/ld+json"}).contents
                jso = json.loads(jso[0])
                jso = jso[0]
                logger.info(jso)

                loc = jso["name"]
                id = jso["branchCode"]
                addr = jso["address"]
                city = addr["addressLocality"]
                state = addr["addressRegion"]
                zip = addr["postalCode"].strip()
                if zip == "":
                    zip = "<MISSING>"
                street = addr["streetAddress"].replace(",", " ").strip()
                lat = jso["location"]["geo"]["latitude"]
                if str(lat) == "None":
                    lat = "<MISSING>"
                long = jso["location"]["geo"]["longitude"]
                if str(long) == "None" or long == "":
                    long = "<MISSING>"
                type = jso["@type"]
                phone = jso["telephone"]
                if phone == "1":
                    phone = "<MISSING>"
                days = jso["openingHoursSpecification"]
                tim = ""
                for day in days:
                    tim += (
                        day["dayOfWeek"]
                        + ": "
                        + day["opens"]
                        + " - "
                        + day["closes"]
                        + " "
                    )
                logger.info(tim)
                yield SgRecord(
                    locator_domain="https://smashburger.com",
                    page_url=url,
                    location_name=loc,
                    street_address=street,
                    city=city,
                    state=state,
                    zip_postal=zip,
                    country_code=country,
                    store_number=id,
                    phone=phone,
                    location_type=type,
                    latitude=lat,
                    longitude=long,
                    hours_of_operation=tim.strip(),
                )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
