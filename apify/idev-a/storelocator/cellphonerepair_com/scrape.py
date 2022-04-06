from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("cellphonerepair")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.cellphonerepair.com/locations/"
locator_domain = "https://www.cellphonerepair.com"
session = SgRequests().requests_retry_session()
max_workers = 12


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetchConcurrentSingle(link):
    page_url = link.a["href"]
    if not page_url.startswith("http"):
        page_url = locator_domain + link.a["href"]
    res = request_with_retries(page_url)
    if res:
        return page_url, res


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    res = session.get(url, headers=_headers)
    if res.status_code == 200:
        return res


def _d(page_url, res, country):
    hours = []
    sp1 = bs(res.text, "lxml")
    for hh in sp1.select("div.store-hours-table div.tableGrid"):
        hours.append(
            f"{hh.select_one('.day').text.strip()}: {hh.select_one('.from').text.strip()}-{hh.select_one('.to').text.strip()}"
        )
    if not hours:
        locID = res.text.split("var locID =")[1].split(";")[0].strip()
        for hh in (
            request_with_retries(
                f"https://cprapi.fpsdv.com/wp-json/cprfe/v1/working-hours/?location_id={locID}"
            )
            .json()["hours"]
            .get("regularHours", [])
        ):
            if hh.get("schema"):
                hours.append(f"{hh['schema']}")
            else:
                hours.append(f"{hh['day']}: closed")

    state = zip_postal = ""
    if sp1.select_one('meta[itemprop="addressRegion"]'):
        state = sp1.select_one('meta[itemprop="addressRegion"]')["content"]
    if sp1.select_one('meta[itemprop="postalCode"]'):
        zip_postal = sp1.select_one('meta[itemprop="postalCode"]')["content"]
    return SgRecord(
        page_url=page_url,
        location_name=sp1.select_one("div.store-full-info h3").text.strip(),
        street_address=sp1.select_one('meta[itemprop="streetAddress"]')[
            "content"
        ].split(",")[0],
        city=sp1.select_one('meta[itemprop="addressLocality"]')["content"],
        state=state,
        zip_postal=zip_postal,
        country_code=country,
        phone=sp1.select_one('span[itemprop="telephone"]').text.strip(),
        locator_domain=locator_domain,
        latitude=sp1.select_one('meta[itemprop="latitude"]')["content"],
        longitude=sp1.select_one('meta[itemprop="longitude"]')["content"],
        hours_of_operation="; ".join(hours),
    )


def _d1(page_url, _, res, country):
    sp1 = bs(res.text, "lxml")
    _addr = []
    for aa in _.select("p"):
        _addr += list(aa.stripped_strings)
    phone = ""
    if _p(_addr[-1]):
        phone = _addr[-1]
        del _addr[-1]
    addr = parse_address_intl(" ".join(_addr))
    hours = [
        ": ".join(hh.stripped_strings) for hh in sp1.select("table.business_hours tr")
    ]
    return SgRecord(
        page_url=page_url,
        location_name=_.h2.text.strip(),
        street_address=_addr[0],
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code=country,
        phone=phone,
        latitude=_["data-lat"],
        longitude=_["data-lng"],
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
    )


def _dd(page_url, _, country):
    _addr = []
    for aa in _.select("p"):
        _addr += list(aa.stripped_strings)
    phone = ""
    if _p(_addr[-1]):
        phone = _addr[-1]
        del _addr[-1]
    addr = parse_address_intl(" ".join(_addr))
    return SgRecord(
        page_url=page_url,
        location_name=_.h2.text.strip(),
        street_address=_addr[0],
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code=country,
        phone=phone,
        latitude=_["data-lat"],
        longitude=_["data-lng"],
        locator_domain=locator_domain,
    )


def fetch_data():
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    prev_country = ""
    for cc in soup.select("div.country"):
        country = cc.text.strip()
        if country != "Regions":
            prev_country = country
        if country == "Regions":
            country = prev_country
        links = cc.find_next_sibling("div", recursive=False).select(
            "div.state-loc-block"
        )
        logger.info(f"{len(links)} found")
        for state_url, res in fetchConcurrentList(links):
            sp1 = bs(res.text, "lxml")
            locations = sp1.select("div.marker")
            if not locations:
                locations = [ll for ll in sp1.select("div.ezcol-one-third") if ll.h3]
            t_locs = []
            for loc in locations:
                if loc.span and "coming soon" in loc.span.text.lower():
                    continue
                if loc.a:
                    t_locs.append(loc)
                else:
                    yield _dd(state_url, loc, country)
            for page_url, res2 in fetchConcurrentList(t_locs):
                yield _d(page_url, res2, country)
            if not locations:
                yield _d(state_url, res, country)

    countries = soup.select("select.int-locations")[0].select("option")
    for link in countries:
        if not link.get("value"):
            continue
        country_url = link["value"]
        logger.info(country_url)
        res = session.get(country_url, headers=_headers)
        sp1 = bs(res.text, "lxml")
        country = link.text.strip()
        locations = sp1.select("div.marker")
        if not locations:
            locations = [ll for ll in sp1.select("div.ezcol-one-third") if ll.h3]
        for _ in locations:
            if not _.a:
                yield _dd(country_url, _, country)
            else:
                page_url = _.a["href"]
                if not page_url.startswith("http"):
                    page_url = locator_domain + _.a["href"]
                res2 = session.get(page_url, headers=_headers)
                yield _d1(page_url, _, res2, country)
        if not locations:
            yield _d1(country_url, _, res, country)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
