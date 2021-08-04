from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sgscrape.sgpostal import parse_address_intl
import os

logger = SgLogSetup().get_logger("lifestance")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

max_workers = 8

DEFAULT_PROXY_URL = "https://groups-RESIDENTIAL,country-US:{}@proxy.apify.com:8000/"


def set_proxies():
    if "PROXY_PASSWORD" in os.environ and os.environ["PROXY_PASSWORD"].strip():

        proxy_password = os.environ["PROXY_PASSWORD"]
        url = (
            os.environ["PROXY_URL"] if "PROXY_URL" in os.environ else DEFAULT_PROXY_URL
        )
        proxy_url = url.format(proxy_password)
        proxies = {
            "https://": proxy_url,
        }
        return proxies
    else:
        return None


session = SgRequests().requests_retry_session()
session.proxies = set_proxies()


def fetchConcurrentSingle(data):
    response = request_with_retries(data.text)
    return data.text, response.text


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
            count = count + 1
            if count % reminder == 0:
                logger.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def request_with_retries(url):
    return session.get(url, headers=_headers)


def fetch_data():
    locator_domain = "https://lifestance.com/"
    base_url = "https://lifestance.com/location-sitemap.xml"
    locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
        "url loc"
    )
    logger.info(f"{len(locations)} locations found")
    for page_url, response in fetchConcurrentList(locations):
        logger.info(f"{page_url}")
        sp1 = bs(response, "lxml")
        addr = parse_address_intl(
            " ".join(sp1.select_one("div.self-center div.p").stripped_strings)
        )
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        _hr = sp1.find("h2", string=re.compile(r"Hours Of Operation"))
        hours = []
        if _hr:
            hours = [
                ":".join(hh.stripped_strings) for hh in _hr.find_next_siblings("div")
            ]
        phone = ""
        if sp1.find("a", href=re.compile(r"tel:")):
            phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
        coord = (
            sp1.select_one("main figure a img")["data-lazy-src"]
            .split("false%7C")[1]
            .split(",+")
        )
        yield SgRecord(
            page_url=page_url,
            location_name=sp1.select_one("h1.h1").text.strip(),
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="US",
            phone=phone,
            locator_domain=locator_domain,
            latitude=coord[0],
            longitude=coord[1],
            hours_of_operation="; ".join(hours).replace("–", "-"),
        )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
        raise
