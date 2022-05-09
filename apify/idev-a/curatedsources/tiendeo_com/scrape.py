from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
from sgpostal.sgpostal import parse_address_intl
import math
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, wait_random, stop_after_attempt
import random
from webdriver_manager.chrome import ChromeDriverManager
import os

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"

logger = SgLogSetup().get_logger("")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://tiendeo.com/"
urls = {
    "Australia": "https://www.tiendeo.com.au/catalogues-sale",
    "Spain": "https://www.tiendeo.com/Folletos-Catalogos",
    "Italy": "https://www.tiendeo.it/Volantino-Catalogo",
    "Mexico": "https://www.tiendeo.mx/Folletos-Catalogos",
    "Brazil": "https://www.tiendeo.com.br/Encartes-Catalogos",
    "Colombia": "https://www.tiendeo.com.co/Folletos-Catalogos",
    "Argentia": "https://www.tiendeo.com.ar/Folletos-Catalogos",
    "India": "https://www.tiendeo.in/Leaflets-Catalogues",
    "France": "https://www.tiendeo.fr/Prospectus-Catalogues",
    "The Netherlands": "https://www.tiendeo.nl/Folders-Catalogi",
    "Germany": "https://www.tiendeo.de/Prospekte-Kataloge",
    "Peru": "https://www.tiendeo.pe/Folletos-Catalogos",
    "Chile": "https://www.tiendeo.cl/Folletos-Catalogos",
    "Portugal": "https://www.tiendeo.pt/Encartes-Catalogos",
    "Russia": "https://www.tiendeo.ru/katalogi-predlojenija",
    "Turkey": "https://www.tiendeo.com.tr/Brosurler-Kataloglar",
    "Polish": "https://www.tiendeo.pl/katalogi-ulotki",
    "Norway": "https://www.tiendeo.no/brosjyrer",
    "Austria": "https://www.tiendeo.at/Prospekte-Kataloge",
    "Sweden": "https://www.tiendeo.se/broschyrer",
    "Ecuador": "https://www.tiendeo.com.ec/folletos-catalogos",
    "Singapore": "https://www.tiendeo.sg/Leaflets-Catalogues",
    "Indonesia": "https://www.tiendeo.co.id/leaflets-catalogues",
    "Malaysia": "https://www.tiendeo.my/leaflets-catalogues",
    "South Africa": "https://www.tiendeo.co.za/leaflets-catalogues",
    "Denmark": "https://www.tiendeo.dk/brochurer-kataloger",
    "Finland": "https://www.tiendeo.fi/esitteet-luettelot",
    "New Zealand": "https://www.tiendeo.co.nz/brochures-catalogues",
    "Japan": "https://www.tiendeo.jp/%E3%83%91%E3%83%B3%E3%83%95%E3%83%AC%E3%83%83%E3%83%88%E2%80%90%E3%82%AB%E3%82%BF%E3%83%AD%E3%82%B0",
    "Greece": "https://www.tiendeo.gr/%CF%86%CF%85%CE%BB%CE%BB%CE%AC%CE%B4%CE%B9%CE%B1-%CE%BA%CE%B1%CF%84%CE%AC%CE%BB%CE%BF%CE%B3%CE%BF%CE%B9",
    "South Korea": "https://www.tiendeo.co.kr/,%EB%B8%8C%EB%A1%9C%EC%8A%88%EC%96%B4-%EC%B9%B4%ED%83%88%EB%A1%9C%EA%B7%B8",
    "Belgium": "https://www.tiendeo.be/fr/prospectus-catalogues",
    "Switzerland": "https://www.tiendeo.ch/prospekte-kataloge",
    "UAE": "https://www.tiendeo.ae/offers-promotions",
    "Ukraine": "https://www.tiendeo.com.ua/aktsii-katalohy",
    "Romania": "https://www.tiendeo.ro/cataloage-oferte",
    "Maroku": "https://www.tiendeo.ma/prospectus-catalogues",
    "Czech Republic": "https://www.tiendeo.cz/letaky-katalogy",
    "Slovakia": "https://www.tiendeo.sk/letaky-katalogy",
    "Hungary": "https://www.tiendeo.hu/akciosujsag-katalogusok",
    "Bulgaria": "https://www.tiendeo.bg/katalog-broshura",
}


user_agents = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 OPR/77.0.4054.172",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.203",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36 Edg/91.0.864.71",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
]

cc = [
    "de",
]

hr_obj = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}


def _time(h, val):
    val = str(val)
    if len(val) == 1:
        val = "0" + val
    return f"{h}:{val}"


max_workers = 64


def fetchSingleStoreIndex(store_index, domain):
    if not store_index.get("link") or not store_index["link"].get("url"):
        return None
    store_index_url = domain + store_index["link"]["url"]
    try:
        navs = json.loads(
            bs(request_with_retries(store_index_url).text, "lxml")
            .select_one("script#__NEXT_DATA__")
            .text
        )["props"]["pageProps"]["queryResult"]["Breadcrumb"]["navigationLinks"]
        if navs:
            store_url = domain + navs[0]["url"]
            res_ss = json.loads(
                bs(request_with_retries(store_url).text, "lxml")
                .select_one("script#__NEXT_DATA__")
                .text
            )["props"]["pageProps"]["queryResult"]["HighLightedCities"]
            if not res_ss["links"]:
                return None
            return [ss for ss in res_ss["links"] if ss]
        else:
            return None
    except:
        return None


def fetchSingleStore(store, domain):
    if not store.get("url"):
        return None
    store_location_url = domain + store["url"]
    logger.info(store_location_url)
    return (
        store,
        json.loads(
            bs(
                request_with_retries(store_location_url).text,
                "lxml",
            )
            .select_one("script#__NEXT_DATA__")
            .text
        )["props"]["pageProps"]["queryResult"],
    )


def fetchConcurrentStoreIndexes(total_list, domain, occurrence=max_workers):
    output = []
    total = len(total_list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(
            fetchSingleStoreIndex, total_list, [domain] * len(total_list)
        ):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def fetchConcurrentStores(total_list, domain, occurrence=max_workers):
    output = []
    total = len(total_list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(
            fetchSingleStore, total_list, [domain] * len(total_list)
        ):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


@retry(stop=stop_after_attempt(7), wait=wait_random(min=10, max=16))
def request_with_retries(page_url):
    with SgRequests(
        proxy_country="de", retries_with_fresh_proxy_ip=7, verify_ssl=False
    ) as session:
        _headers["User-Agent"] = random.choice(user_agents)
        sp1 = session.get(page_url, headers=_headers)
        if not sp1.text.strip():
            raise Exception
        return sp1


def _d(loc, domain, country):
    if type(loc["url"]) == dict:
        page_url = domain + loc["url"]["url"]
    else:
        page_url = domain + loc["url"]

    logger.info(page_url)
    try:
        _ = json.loads(
            bs(request_with_retries(page_url).text, "lxml")
            .select_one("script#__NEXT_DATA__")
            .text
        )["props"]["pageProps"]["queryResult"]["Store"]
    except Exception as err:
        logger.info(str(err))
        return None
    raw_address = f"{_['address']}, {_['city']}"
    if _["postalCode"]:
        raw_address += f", {_['postalCode']}"
    raw_address += f", {country}"
    addr = parse_address_intl(raw_address)
    hours = []
    if _["schedules"]:
        for hh in _["schedules"]:
            day = hr_obj.get(str(hh["day"]))
            times = _time(hh["openingHour"], hh["openingMinute"])
            hours.append((f"{day}: {times}"))

    city = addr.city
    if city and city.lower() == "city":
        city = ""
    state = addr.state
    if state and state == _.get("postalCode"):
        state = ""
    return SgRecord(
        page_url=page_url,
        store_number=_["id"],
        location_name=_["name"],
        street_address=_["address"],
        city=city,
        state=state,
        zip_postal=_.get("postalCode"),
        country_code=country,
        phone=_["phone"],
        latitude=_["lat"],
        longitude=_["lon"],
        location_type=_["retailer"]["category"]["shortName"],
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
        raw_address=raw_address,
    )


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


def fetch_data():
    driver = get_driver()
    with SgRequests(proxy_country="us") as session:
        for country, base_url in urls.items():
            logger.info(f"[{country}] {base_url}")
            domain = "/".join(base_url.split("/")[:-1])
            res_sd = json.loads(
                bs(session.get(base_url, headers=_headers).text, "lxml")
                .select_one("script#__NEXT_DATA__")
                .text
            )["props"]["pageProps"]["queryResult"]["Retailers"]
            if not res_sd.get("nodes"):
                continue
            store_indices = [ss for ss in res_sd["nodes"] if ss]
            for store_index in store_indices:
                if not store_index.get("link") or not store_index["link"].get("url"):
                    continue
                store_index_url = domain + store_index["link"]["url"]
                try:
                    driver.get(store_index_url)
                    navs = json.loads(
                        bs(driver.page_source, "lxml")
                        .select_one("script#__NEXT_DATA__")
                        .text
                    )["props"]["pageProps"]["queryResult"]["Breadcrumb"][
                        "navigationLinks"
                    ]
                    if not navs:
                        continue
                    store_url = domain + navs[0]["url"]
                except Exception as err:
                    logger.info(str(err))
                res_ss = json.loads(
                    bs(request_with_retries(store_url).text, "lxml")
                    .select_one("script#__NEXT_DATA__")
                    .text
                )["props"]["pageProps"]["queryResult"]["HighLightedCities"]
                if not res_ss["links"]:
                    continue
                stores = [ss for ss in res_ss["links"] if ss]
                for store in stores:
                    if not store.get("url"):
                        continue
                    store_location_url = domain + store["url"]
                    logger.info(store_location_url)
                    try:
                        results = json.loads(
                            bs(
                                request_with_retries(store_location_url).text,
                                "lxml",
                            )
                            .select_one("script#__NEXT_DATA__")
                            .text
                        )["props"]["pageProps"]["queryResult"]
                    except Exception as err:
                        logger.info(str(err))

                    if results.get("StoresByCity"):
                        locations = [
                            ll for ll in results["StoresByCity"]["nodes"] if ll
                        ]
                        if not locations:
                            continue
                        for loc in locations:
                            yield _d(loc, domain, country)
                    else:
                        yield _d(store, domain, country)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
