from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import urllib.parse
import re

DOMAIN = "littlesheep.com"
LOCATION_URL = "http://www.littlesheep.com/ResTuarant"
DATA_URL = "http://www.littlesheep.com/ResTuarant/getEndList"
DATA_URL_PAGE = "http://www.littlesheep.com/ResTuarant/_index"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


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


def get_city(_city):
    try:
        if _city is not None and _city != MISSING:
            data = parse_address_intl(_city)
            city = data.city or MISSING
            return city
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_international_stores(payload, num=0):
    num += 1
    try:
        stores = bs(
            session.post(DATA_URL_PAGE, headers=HEADERS, data=payload).content, "lxml"
        ).select("ul li")
    except:
        if num <= 5:
            return get_international_stores(payload, num)
    return stores


def get_city_id(city_name, num=0):
    num += 1
    try:
        cookie = {"iplocation": urllib.parse.quote(city_name + "|0|0")}
        r = session.get(LOCATION_URL, cookies=cookie)
        store = bs(r.content, "lxml")
        city_id = re.search(
            r"var cityId=(\d+);",
            store.find("script", string=re.compile(r"var cityId=.*")).string,
        ).group(1)
    except:
        if num <= 5:
            return get_city_id(city_name, num)
    return city_id


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(DATA_URL)
    stores = soup.select("ul li")
    for row in stores:
        info = (
            row["onclick"]
            .replace("ClickStore('", "")
            .replace("')", "")
            .replace("'", "")
            .split("|")
        )
        location_name = info[1]
        raw_address = info[2]
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = info[3].split(",")[0].split("\n")[0]
        country_code = "CN"
        hours_of_operation = MISSING
        store_number = info[3].split(",")[1]
        location_type = MISSING
        coord = info[0].split(",")
        if len(coord[0].split(".")[0]) < 3 or float(coord[0]) < 80:
            latitude = coord[0]
            longitude = coord[1]
        else:
            latitude = coord[1]
            longitude = coord[0]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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

    log.info("Get international locations...")
    soup = pull_content(LOCATION_URL)
    titles = soup.select("div.this_f_letters a")
    for name in titles:
        city_id = get_city_id(name.text.strip())
        log.info(f"Search locations for city_id => {city_id}")
        payload = {
            "SearchStore": "",
            "PageIndex": "1",
            "PageSize": "1000",
            "CityId": city_id,
        }
        stores = get_international_stores(payload)
        for row in stores:
            info = (
                row["onclick"]
                .replace("ClickStore('", "")
                .replace("')", "")
                .replace("'", "")
                .split("|")
            )
            location_name = info[1]
            raw_address = info[2]
            street_address, city, state, zip_postal = getAddress(raw_address)
            street_address = street_address.replace('"', "'")
            phone = info[3].split(",")[0].split("\n")[0]
            if "日本" in row["onclick"]:
                country_code = "JP"
            elif "印度尼西亚" in row["onclick"]:
                country_code = "ID"
            elif "印度尼西亚" in row["onclick"]:
                country_code = "ID"
            elif "金边" in row["onclick"]:
                country_code = "Cambodia"
            elif "蒙古" in row["onclick"]:
                country_code = "Mongol "
            elif "澳大利亚" in row["onclick"]:
                country_code = "AU"
            elif "新加坡" in row["onclick"]:
                country_code = "SG"
            elif "新西兰" in row["onclick"]:
                country_code = "NZ"
            elif "Jakarta" in row["onclick"]:
                if "10210" in street_address:
                    zip_postal = "10210"
                    street_address = street_address.replace("10210", "").strip()
                country_code = "ID"
            elif "Phnom Penh" in row["onclick"]:
                country_code = "Cambodia"
                city = "Phnom Penh"
            else:
                country_code = MISSING
            hours_of_operation = MISSING
            store_number = info[3].split(",")[1]
            location_type = MISSING
            coord = info[0].split(",")
            try:
                if len(coord[0].split(".")[0]) < 3 or float(coord[0]) < 80:
                    latitude = coord[0]
                    longitude = coord[1]
                else:
                    latitude = coord[1]
                    longitude = coord[0]
            except:
                latitude = MISSING
                longitude = MISSING
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=LOCATION_URL,
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
