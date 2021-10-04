import re
import json
from bs4 import BeautifulSoup as bs
from lxml import etree
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl

DOMAIN = "slimchickens.com"
BASE_URL = "https://www.slimchickens.com/"
LOCATION_URL = "https://slimchickens.com/location-menus/"
UK_LOCATION_URL = "https://www.slimchickens.co.uk/location-menus/"
API_URL = "https://storerocket.io/api/user/56wpZ22pAn/locations?radius=50&units=miles"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

session = SgRequests()

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code != 200:
        return False
    soup = bs(req.content, "lxml")
    return soup


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


def get_latlong(url):
    coord = re.search(r"!2d(-[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
    if not coord:
        coord = re.search(r"!2d([\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
        if not coord:
            return "<MISSING>", "<MISSING>"
        return coord.group(1), coord.group(2)
    return coord.group(2), coord.group(1)


def fetch_data():
    data = session.get(API_URL, headers=HEADERS).json()
    all_locations = data["results"]["locations"]
    for row in all_locations:
        page_url = BASE_URL + "location/" + row["slug"]
        loc_response = session.get(page_url, headers=HEADERS)
        if loc_response.status_code == 200:
            loc_dom = etree.HTML(loc_response.text)
            if loc_dom.xpath('//h1[contains(text(), "Coming Soon")]'):
                continue
        location_name = row["name"]
        raw_address = row["display_address"]
        if "troy-mo-31-the-plaza-63379" in row["slug"]:
            street_address = "31 The Plaza"
            city = "Troy"
            state = "MO"
            zip_postal = "63379"
        else:
            street_address, city, state, zip_postal = getAddress(raw_address)
        if zip_postal == MISSING:
            zip_postal = row["slug"].split("-")[-1]
        hours_of_operation = [e for e in row["fields"] if e["name"] == "Hours"]
        if not hours_of_operation:
            req = session.get(page_url, headers=HEADERS)
            if req.status_code != 200:
                continue
            loc_dom = etree.HTML(req.text)
            raw_data = loc_dom.xpath('//div[@id="MapAddress"]/p/text()')
            raw_data = [e.strip() for e in raw_data]

            data = loc_dom.xpath(
                '//script[contains(text(), "maplistFrontScriptParams")]/text()'
            )
            if not data:
                continue
            data = re.findall("tParams =(.+);", data[0])[0]
            data = json.loads(data)
            poi = json.loads(data["location"])
            location_name = poi["title"]
            if "Coming Soon" in location_name:
                continue
        hours_of_operation = (
            hours_of_operation[0]["pivot_field_value"].replace("</br>", " ")
            if hours_of_operation
            else SgRecord.MISSING
        )
        phone = [e for e in row["fields"] if e["name"] == "Phone"]
        phone = phone[0]["pivot_field_value"] if phone else SgRecord.MISSING
        country_code = "US" if len(row["country"]) < 1 else row["country"]
        store_number = MISSING
        location_type = "slimchickens-" + country_code
        latitude = row["lat"]
        longitude = row["lng"]
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

    # Scrape UK
    soup = pull_content(UK_LOCATION_URL)
    links = soup.find("li", {"id": "nav-menu-item-11723"}).find_all("a")
    del links[0]
    for row in links:
        if "coming-soon" in row["href"]:
            continue
        if "slimchickens.co.uk" not in row["href"]:
            page_url = "http://www.slimchickens.co.uk" + row["href"]
        else:
            page_url = row["href"]
        content = pull_content(page_url)
        location_name = content.find(
            "div", {"class": "title_subtitle_holder_inner"}
        ).text.strip()
        raw_address = (
            content.find("div", {"id": "MapAddress"})
            .get_text(strip=True, separator=",")
            .strip()
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = (
            content.find(
                re.compile(r"h4|strong"), text=re.compile(r"PHONE:|PHONE:&nbsp;")
            )
            .find_next(re.compile(r"p|div"))
            .text.strip()
        )
        if phone == "TBC":
            phone = MISSING
        hours_of_operation = (
            content.find(
                re.compile(r"h4|strong"), text=re.compile(r"HOURS:|HOURS:&nbsp;")
            )
            .parent.get_text(strip=True, separator=",")
            .replace("HOURS:,", "")
            .strip()
        )
        country_code = "UK"
        store_number = MISSING
        location_type = "slimchickens-" + country_code
        try:
            map_link = content.find("iframe", {"src": re.compile(r"\/maps\/embed\?")})[
                "src"
            ]
            latitude, longitude = get_latlong(map_link)
        except:
            latitude = MISSING
            longitude = MISSING
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
