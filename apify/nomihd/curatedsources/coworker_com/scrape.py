from sgpostal.sgpostal import parse_address_intl
from lxml import html
import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton

website = "https://www.coworker.com"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

headers_post = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)

states = {
    "alabama": "al",
    "ala": "al",
    "alaska": "ak",
    "alas": "ak",
    "arizona": "az",
    "ariz": "az",
    "arkansas": "ar",
    "ark": "ar",
    "california": "ca",
    "calif": "ca",
    "cal": "ca",
    "colorado": "co",
    "colo": "co",
    "col": "co",
    "connecticut": "ct",
    "conn": "ct",
    "delaware": "de",
    "del": "de",
    "district of columbia": "dc",
    "florida": "fl",
    "fla": "fl",
    "flor": "fl",
    "georgia": "ga",
    "ga": "ga",
    "hawaii": "hi",
    "idaho": "id",
    "ida": "id",
    "illinois": "il",
    "ill": "il",
    "indiana": "in",
    "ind": "in",
    "iowa": "ia",
    "kansas": "ks",
    "kans": "ks",
    "kan": "ks",
    "kentucky": "ky",
    "ken": "ky",
    "kent": "ky",
    "louisiana": "la",
    "maine": "me",
    "maryland": "md",
    "massachusetts": "ma",
    "mass": "ma",
    "michigan": "mi",
    "mich": "mi",
    "minnesota": "mn",
    "minn": "mn",
    "mississippi": "ms",
    "miss": "ms",
    "missouri": "mo",
    "montana": "mt",
    "mont": "mt",
    "nebraska": "ne",
    "nebr": "ne",
    "neb": "ne",
    "nevada": "nv",
    "nev": "nv",
    "new-hampshire": "nh",
    "new-jersey": "nj",
    "new-mexico": "nm",
    "n mex": "nm",
    "new m": "nm",
    "new-york": "ny",
    "north-carolina": "nc",
    "north-dakota": "nd",
    "n dak": "nd",
    "ohio": "oh",
    "oklahoma": "ok",
    "okla": "ok",
    "oregon": "or",
    "oreg": "or",
    "ore": "or",
    "pennsylvania": "pa",
    "penn": "pa",
    "rhode-island": "ri",
    "south-carolina": "sc",
    "south-dakota": "sd",
    "s dak": "sd",
    "tennessee": "tn",
    "tenn": "tn",
    "texas": "tx",
    "tex": "tx",
    "utah": "ut",
    "vermont": "vt",
    "virginia": "va",
    "washington": "wa",
    "wash": "wa",
    "west virginia": "wv",
    "w va": "wv",
    "wisconsin": "wi",
    "wis": "wi",
    "wisc": "wi",
    "wyoming": "wy",
    "wyo": "wy",
    "washington-dc": "dc",
}


def request_with_retries(url):
    response = session.get(url, headers=headers)
    return html.fromstring(response.text, "lxml")


def request_post_pages(city_id, country_id, page_num):
    response = session.post(
        f"{website}/ajax/spaces",
        headers=headers_post,
        data=f"city_id={city_id}&country_id={country_id}&page_num={page_num}",
    )
    response = json.loads(response.text)
    return response["numSpaces"], response["mapSpaces"]


def fetch_cities():
    body = request_with_retries(f"{website}/office-space/cities")
    city_urls = body.xpath('//a[contains(@href, "/office-space/")]/@href')[1:-1]
    state_keys = states.keys()

    for index in range(len(city_urls)):
        city_urls[index] = city_urls[index].replace("office-space", "search")

        if "united-states" in city_urls[index]:
            parts = city_urls[index].split("/")
            if parts[5] in state_keys:
                city_urls[index] = city_urls[index].replace(
                    f"/{parts[5]}/", f"/{states[parts[5]]}/"
                )
    return city_urls


def fetch_pages(city_url):
    body = request_with_retries(city_url)
    city_id = body.xpath('//input[@id="city_id"]/@value')[0]
    country_id = body.xpath('//input[@id="country_id"]/@value')[0]
    all_stores = []
    page = 0
    while True:
        page = page + 1
        total_stores, stores = request_post_pages(city_id, country_id, page)
        for store in stores:
            page_url = store["profile_url_full"]
            location = store["location"]

            raw_address = (location["address_1"] + " " + location["address_2"]).strip()
            if location["city_name"]:
                raw_address = raw_address + ", " + location["city_name"]
            if location["state_code"]:
                raw_address = raw_address + ", " + location["state_code"]

            all_stores.append(
                {
                    "store_number": store["id"],
                    "location_name": store["name"],
                    "page_url": page_url,
                    "raw_address": raw_address,
                    "country_code": location["country_code"],
                    "latitude": location["lat"],
                    "longitude": location["lng"],
                }
            )
        if total_stores < page * 10:
            break
    return all_stores


def stringify_nodes(body, xpath):
    nodes = body.xpath(xpath)
    values = []
    for node in nodes:
        for text in node.itertext():
            text = text.strip()
            if text:
                values.append(text)

    if len(values) == 0:
        return MISSING
    return " ".join((" ".join(values)).split())


def get_hours_of_operation(url):
    try:
        body = request_with_retries(url)
        return stringify_nodes(body, '//div[contains(@class, "space-member-times")]')
    except Exception as e:
        log.error(f"{url} can't get hoo e={e}")
        return MISSING


def get_address(raw_address):
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
        log.info(f"Address Error: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    city_urls = fetch_cities()
    log.info(f"Total cities = {len(city_urls)}")
    city_count = 0
    page_count = 0

    for city_url in city_urls:
        city_count = city_count + 1
        try:
            stores = fetch_pages(city_url)
            log.info(f"{city_count}. From {city_url} page urls = {len(stores)}")
        except Exception as e:
            log.error(f"{city_count}. Can't find {city_url} e={e}")
            continue

        for store in stores:
            page_count = page_count + 1
            log.info(f"  {page_count}. scrapping {store['location_name']}")
            hours_of_operation = get_hours_of_operation(store["page_url"])
            street_address, city, state, zip_postal = get_address(store["raw_address"])

            yield SgRecord(
                locator_domain=website,
                location_type=MISSING,
                store_number=store["store_number"],
                page_url=store["page_url"],
                location_name=store["location_name"],
                country_code=store["country_code"],
                latitude=store["latitude"],
                longitude=store["longitude"],
                raw_address=store["raw_address"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info(f"Start scrapping {website} ...")
    CrawlStateSingleton.get_instance().save(override=True)
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
