from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "jimmyspizza.com"
BASE_URL = "https://www.jimmyspizza.com/"
LOCATION_URL = "https://jimmyspizza.com/locator.php"
API_URL = "https://jimmyspizza.com/ajax.php"
HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_hoo(url):
    soup = pull_content(url)
    hoo_content = soup.find("div", id=re.compile(r"dine-in-\d"))
    if not hoo_content:
        hoo_content = soup.find("div", id=re.compile(r"curbside-\d"))
    if not hoo_content:
        hoo_content = soup.find("div", id="-0")
    hours = (
        hoo_content.find("table")
        .get_text(strip=True, separator=",")
        .replace("day,", "day: ")
    ).strip()
    return hours


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    state_list = soup.find("select", id="state").find_all("option")
    for val_state in state_list:
        payload = {"state": val_state["value"], "tool": "get-cities"}
        get_cities = session.post(API_URL, headers=HEADERS, data=payload).text
        cities = bs(" ".join(get_cities.split()), "lxml").find_all(
            "option", value=re.compile(r"\D+")
        )
        for val_city in cities:
            page_url = BASE_URL + val_city.text.lower().replace(" ", "")
            log.info("Pull content => " + page_url)
            req = session.get(page_url)
            store = bs(req.content, "lxml")
            location_name = val_city.text.strip()
            raw_address = val_city["value"].split("++")[0]
            street_address, city, state, zip_postal = getAddress(raw_address)
            phone = val_city["value"].split("++")[1]
            curr_link = str(req.url)
            if (
                "/sterling/" in curr_link
                or "/rice/" in curr_link
                or "silverbay/" in curr_link
                or "stcharles" in curr_link
                or "winsted" in curr_link
            ):
                cont = store.select_one("div.header-text").text.split("\n")
                hours = ""
                take_more = False
                for c in cont:
                    if "HOURS" in c:
                        take_more = True
                    if take_more:
                        hours += c + " "
            elif (
                "jimmyspizzaannandale" in curr_link
                or "jimmyspizzacoldspring" in curr_link
                or "jimmyspizzahawley" in curr_link
                or "immyspizzalitchfield" in curr_link
            ):
                days = store.select("div.p.af")
                hours = ""
                for day in days:
                    hours += day.text + " "
            elif "jimmyspizzahutch" in curr_link:
                hours = "Lunch Mon - Fri 11am-1:30pm Dinner Mon - Thurs 4pm-9pm Fri - Sat 4pm-10pm ​Closed Sunday"

            elif "jimmysaberdeen" in curr_link:

                hours = "Monday – Sunday: 4pm – 9pm"
            else:
                hours = store.find("div", {"class": "sub-text"})
                if hours:
                    if len(hours) == 1:
                        hours = hours.text.replace("STORE HOURS:", "").replace(
                            "\n", " "
                        )
                    else:
                        try:
                            hours = (
                                store.find("strong", text=re.compile(r"Summer Hours.*"))
                                .parent.text.replace("STORE HOURS:", "")
                                .replace("\n", " ")
                            )
                        except:
                            hours = (
                                "Sunday-Thursday 4pm-10pm Friday & Saturday 4pm-11pm"
                            )
                else:
                    hours = MISSING
            hours_of_operation = (
                re.sub(
                    r"^:|OUR HOURS:|STORE HOURS|STOREHOURS:|\(Delivery available\s+\d{1,2}:\d{1,2}am-\d{1,2}:\d{1,2}pm\)|\(including buffet\)|\(\)|\n",
                    "",
                    hours,
                )
                .replace("\n", " ")
                .replace("\u00A0", "")
                .replace("\u200b", "")
                .strip()
            )
            country_code = "US"
            store_number = MISSING
            latitude = MISSING
            longitude = MISSING
            location_type = MISSING
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
                raw_address=raw_address,
            )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
