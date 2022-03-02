import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import html


DOMAIN = "bricocenter.it"
BASE_URL = "https://www.bricocenter.it"
LOCATION_URL = "https://www.bricocenter.it/it/punti-vendita"
API_URL = "https://www.bricocenter.it/it/ajax-search-pdv?lat=&lon=&ser=&_=1645869228755"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()
days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_hoo(content):
    hoo = ""
    hours_content = content.find("table", {"class": "opening-time"})
    hours = hours_content.find("tbody").find_all("tr")
    starts = hours[0].find_all("td")[1:]
    ends = hours[1].find_all("td")[1:]
    for i in range(len(days)):
        if starts[i].text.replace("dalle", "").strip() == "-":
            hour = "CLOSED"
        else:
            if "dalle" not in starts[i].text:
                hour = starts[i].text.strip() + "," + ends[i].text.strip()
            else:
                hour = (
                    starts[i].text.replace("dalle ", "")
                    + " -"
                    + ends[i].text.replace("alle", "")
                ).strip()
        hoo += days[i] + ": " + hour + ", "
    hoo = re.sub(r"-?\s?\s?\s?Puoi acquistare anche in e-commerce!?", "", hoo).strip()
    return hoo.strip().rstrip(",")


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()["data"]
    for row in data["pdv"]:
        page_url = BASE_URL + row["url"]
        store = pull_content(page_url)
        location_name = html.unescape(row["city"])
        city = location_name
        state = html.unescape(row["prov"])
        zip_postal = row["cap"]
        street_address = html.unescape(
            " ".join(
                re.sub(
                    r",?\s?" + city + r"|,?\s?" + state + r"|\(.*\)|" + zip_postal,
                    "",
                    row["address"],
                )
                .strip()
                .split()
            )
        ).replace('"', "'")
        country_code = "IT"
        phone = re.sub(
            r"[a-zA-Z].*|\/ \d{4} \d{7}|----.*", "", row["tel"].split("<br>")[0]
        ).strip()
        store_number = row["id"]
        hours_of_operation = get_hoo(store)
        location_type = MISSING
        latitude = row["lat"]
        longitude = row["lon"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
