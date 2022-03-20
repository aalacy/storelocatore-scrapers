from sgrequests import SgRequests
from sgscrape.pause_resume import CrawlStateSingleton
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from typing import Iterable, Tuple, Callable
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import SgLogSetup
from lxml import html
import time
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


class ExampleSearchIteration(SearchIteration):
    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

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
                for _ in json_data:

                    ln = _["name"] or ""
                    tel = _["telephone"] or ""
                    tel = good_phone(tel)
                    staraw = _["address"]["streetAddress"] or ""
                    sta, zc = get_sta_zc(_)
                    state = ""
                    if "addressRegion" in _:
                        state = _["address"]["addressRegion"] or ""
                    city = _["address"]["areaServed"] or ""
                    cc = _["address"]["addressCountry"] or ""
                    lat = _["geo"]["latitude"] or ""
                    lng = _["geo"]["longitude"] or ""
                    lt = ""
                    hoo = fix_hours(_["openingHours"])
                    raw_address = staraw
                    DOMAIN = "clubmonaco_com"
                    found_location_at(float(lat), float(lng))
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
                    yield item


if __name__ == "__main__":
    CrawlStateSingleton.get_instance().save(override=True)
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=300,
    )
    dedupe_dict = {
        SgRecord.Headers.RAW_ADDRESS,
        SgRecord.Headers.LATITUDE,
        SgRecord.Headers.LONGITUDE,
    }

    with SgWriter(
        SgRecordDeduper(
            SgRecordID(dedupe_dict),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        all_countries = get_country_list()
        logger.info(f"Countries to be crawled: {all_countries}")
        # Strange:  DynamicZipSearch returns lat_lng instead of
        # postal code. therefore, DynamicGeoSearch has been used.
        # China-based countries - CN, HK, MO, and TW
        # The rest of the world includes CA, KR, SE, SG, GB, US
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=all_countries,
        )

        for rec in par_search.run():
            writer.write_row(rec)
