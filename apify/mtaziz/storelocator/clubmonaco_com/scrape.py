from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
import json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


LOCATOR_URL = "https://www.clubmonaco.com/en/StoreLocator"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("clubmonaco_com")
MAX_WORKERS = 10


api_endpoint_url = "https://www.clubmonaco.com/on/demandware.store/Sites-ClubMonaco_US-Site/en_US/Stores-ViewResults"
hdr_noncookies = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "origin": "https://www.clubmonaco.com",
    "accept": "*/*",
}

hdr_noncookies["referer"] = LOCATOR_URL


def get_sta_zc(_):
    st = _["address"]["streetAddress"].split(",")
    sta = ""
    zc = ""
    if len(st) == 2:
        sta = st[0]
        zc = st[1]
    if len(st) == 3:
        sta = st[0] + ", " + st[1]
        zc = st[-1]
    if len(st) == 1:
        sta = st
        zc = ""
    if len(st) == 4:
        sta = st[0] + ", " + st[1] + ", " + st[2]
        zc = st[-1]
    return sta, zc


def fix_hours(x):
    x = (
        x.replace("</p>\n", "; ")
        .replace("<p>", "")
        .replace("\n", "")
        .replace("</p>", "")
        .replace("<br />", "; ")
        .replace("&nbsp;", " ")
        .replace("</br></br>", "")
        .replace("</br>", "; ")
        .replace(";  ;", ";")
    )
    if "Curb" in x:
        x = "".join(x.split("Curb")[:-1])
    return x


def good_phone(x):
    x = x.replace("-", "")
    if "Curb" in x:
        x = "".join(x.split("Curb")[:-1])
    if "WedSun" in x:
        x = x.replace("WedSun", "")
    return x


def get_country_list():
    hdr_countrylist = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "origin": "https://www.clubmonaco.com",
        "accept": "*/*",
        "referer": "https://www.clubmonaco.com/en/StoreLocator",
    }
    with SgRequests() as h:
        r = h.get(LOCATOR_URL, headers=hdr_countrylist)
        txt = r.text
        sel_country_list = html.fromstring(txt, "lxml")
        labels = sel_country_list.xpath(
            '//div[contains(@class, "dwfrm_storelocator_country")]/div/select/option'
        )
        countries = {}
        for l in labels:
            country_code_v = "".join(l.xpath("./@value"))
            if country_code_v:
                label = "".join(l.xpath("./@label"))
                country_code_v = "".join(l.xpath("./@value"))
                countries[label] = country_code_v
        country_list = []
        for k, v in countries.items():
            country_list.append(v)
        country_list = sorted(country_list)
        return country_list


countries_to_be_crawled = {
    "Canada": ["CA", "CANADA"],
    "Mainland China": ["CN", "CHINA"],
    "Hong Kong SAR, China": ["HK", "HONG_KONG"],
    "Korea": ["KR", "KOREA_S"],
    "Macao SAR, China": ["MO", "MACAO"],
    "Sweden": ["SE", "SWEDEN"],
    "Singapore": ["SG", "SINGAPORE"],
    "Taiwan Region": ["TW", "TAIWAN"],
    "United Kingdom": ["GB", "BRITAIN"],
    "United States": ["US", "USA"],
}

logger.info(f"Detailed Countries to be crawled: {countries_to_be_crawled}")  # noqa


def fetch_records(coord, search, current_country, sgw: SgWriter):
    lat_search, lng_search = coord
    api_endpoint_url = "https://www.clubmonaco.com/on/demandware.store/Sites-ClubMonaco_US-Site/en_US/Stores-ViewResults"
    latlng_s = str(lat_search) + "," + str(lng_search)
    data_params = {
        "country": current_country,
        "postal": latlng_s,
        "radius": "300",
    }
    logger.info(f"data_params: {data_params}")
    with SgRequests() as http:
        try:
            rpost_sg = http.post(
                api_endpoint_url, data=data_params, headers=hdr_noncookies
            )
            logger.info(f"HTTP Status Code: {rpost_sg.status_code}")
        except:
            return

        text = rpost_sg.text
        logger.info(f"length: {len(text)}")
        if not text:
            return
        else:
            sel = html.fromstring(rpost_sg.text, "lxml")
            js = sel.xpath(
                '//script[contains(@type, "application/ld+json") and contains(text(), "store")]/text()'
            )
            js = "".join(js)
            js = json.loads(js)
            json_data = js["store"]
            found = len(json_data)
            logger.info(f"Total Store Found: {found}")
            if not json_data:
                return
            else:
                for _ in json_data:
                    ln = _["name"] or ""
                    tel = _["telephone"] or ""
                    tel = good_phone(tel)
                    staraw = _["address"]["streetAddress"] or ""
                    sta, zc = get_sta_zc(_)
                    state = ""
                    if "addressRegion" in _["address"]:
                        state = _["address"]["addressRegion"] or ""
                    city = ""
                    if "areaServed" in _["address"]:
                        city = _["address"]["areaServed"] or ""
                    cc = _["address"]["addressCountry"] or ""
                    lat = _["geo"]["latitude"] or ""
                    lng = _["geo"]["longitude"] or ""
                    lt = ""
                    hoo = fix_hours(_["openingHours"])
                    raw_address = staraw
                    DOMAIN = "clubmonaco_com"
                    search.found_location_at(float(lat), float(lng))
                    item = SgRecord(
                        locator_domain=DOMAIN,
                        page_url="",
                        location_name=ln,
                        street_address=sta,
                        city=city,
                        state=state,
                        zip_postal=zc,
                        country_code=cc,
                        store_number="",
                        phone=tel,
                        location_type=lt,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hoo,
                        raw_address=raw_address,
                    )
                    sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    logger.info("Started")

    search_us = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=300,
        granularity=Grain_8(),
        use_state=False,
    )
    country_us = search_us.current_country().upper()

    search_gb = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        expected_search_radius_miles=300,
        granularity=Grain_8(),
        use_state=False,
    )
    country_gb = search_gb.current_country().upper()

    search_ca = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        expected_search_radius_miles=300,
        granularity=Grain_8(),
        use_state=False,
    )
    country_ca = search_ca.current_country().upper()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_us = [
            executor.submit(fetch_records, latlng, search_us, country_us, sgw)
            for latlng in search_us
        ]
        tasks.extend(task_us)

        task_gb = [
            executor.submit(fetch_records, latlng, search_gb, country_gb, sgw)
            for latlng in search_gb
        ]
        tasks.extend(task_gb)

        task_ca = [
            executor.submit(fetch_records, latlng, search_ca, country_ca, sgw)
            for latlng in search_ca
        ]
        tasks.extend(task_ca)

        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
