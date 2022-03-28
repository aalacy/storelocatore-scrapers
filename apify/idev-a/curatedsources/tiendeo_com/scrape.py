from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
from sgpostal.sgpostal import parse_address_intl
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://tiendeo.com/"
urls = {
    "US": "https://www.tiendeo.us/Brochures-Catalogs",
    "Canada": "https://www.tiendeo.ca/Leaflefts-Catalogues",
    "UK": "https://www.tiendeo.co.uk/Leaflets-Catalogues",
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
    store_index_url = domain + store_index["link"]["url"]
    try:
        store_url = (
            domain
            + json.loads(
                bs(
                    request_with_retries(store_index_url).text,
                    "lxml",
                )
                .select_one("script#__NEXT_DATA__")
                .text
            )["props"]["pageProps"]["queryResult"]["Breadcrumb"]["navigationLinks"][0][
                "url"
            ]
        )
        return store_url
    except:
        return None


def fetchSingleStore(store, domain):
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


def fetchConcurrentStoreIndex(list, domain):
    fetchConcurrentList(list, fetchSingleStoreIndex, domain)


def fetchConcurrentStore(list, domain):
    fetchConcurrentList(list, fetchSingleStore, domain)


def fetchConcurrentList(list, fetchSingle, domain, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchSingle, list, [domain] * len(list)):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    with SgRequests(proxy_country="us") as session:
        return session.get(url, headers=_headers)


def _d(loc, domain, country):
    with SgRequests(proxy_country="us") as session:
        if type(loc["url"]) == dict:
            page_url = domain + loc["url"]["url"]
        else:
            page_url = domain + loc["url"]

        logger.info(page_url)
        _ = json.loads(
            bs(session.get(page_url, headers=_headers).text, "lxml")
            .select_one("script#__NEXT_DATA__")
            .text
        )["props"]["pageProps"]["queryResult"]["Store"]
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
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
            raw_address=raw_address,
        )


def fetch_data():
    with SgRequests(proxy_country="us") as session:
        for country, base_url in urls.items():
            logger.info(f"[{country}] {base_url}")
            domain = "/".join(base_url.split("/")[:-1])
            store_indices = json.loads(
                bs(session.get(base_url, headers=_headers).text, "lxml")
                .select_one("script#__NEXT_DATA__")
                .text
            )["props"]["pageProps"]["queryResult"]["Retailers"]["nodes"]
            for store_url in fetchConcurrentStoreIndex(store_indices, domain):
                if not store_url:
                    continue
                logger.info(f"[{country}] {store_url}")
                stores = json.loads(
                    bs(session.get(store_url, headers=_headers).text, "lxml")
                    .select_one("script#__NEXT_DATA__")
                    .text
                )["props"]["pageProps"]["queryResult"]["HighLightedCities"]["links"]
                for store, results in fetchConcurrentStore(stores, domain):
                    if results.get("StoresByCity"):
                        locations = results["StoresByCity"]["nodes"]
                        for loc in locations:
                            yield _d(loc, domain, country)
                    else:
                        yield _d(store, domain, country)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
