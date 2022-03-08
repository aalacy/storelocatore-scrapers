from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("kfcvietnam")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "csrf_cookie_name=61bd10cf132c6e999e002e1975c6ab7b; _gcl_au=1.1.1616132573.1628762764; _gid=GA1.3.1707762538.1628762765; _fbp=fb.2.1628762767016.1864041207; active_province=1132; kfcnew_session=bdk2l41sig2209drj0iruhbqkgt92dg1; kfcvietnam_com_vn_tracking=%7B%22first_url%22%3A%22https%3A%5C%2F%5C%2Fkfcvietnam.com.vn%5C%2Fvi%5C%2Fnha-hang.html%22%2C%22num_visit%22%3A7%2C%22num_referrer%22%3A0%7D; _ga_SDKE88TWBN=GS1.1.1628762772.1.1.1628763178.0; _ga=GA1.3.1668218562.1628762763; _ga_CS6ZM3JC91=GS1.1.1628762762.1.1.1628763204.29",
    "Host": "kfcvietnam.com.vn",
    "Origin": "https://kfcvietnam.com.vn",
    "Referer": "https://kfcvietnam.com.vn/vi/nha-hang.html",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

base_url = "https://kfcvietnam.com.vn/vi/find-a-kfc.html"
locator_domain = "https://kfcvietnam.com.vn"
detail_url = "https://kfcvietnam.com.vn/vi/load_restaurant"
session = SgRequests()
max_workers = 2


def fetchConcurrentSingle(link):
    data = {
        "csrf_site_name": "61bd10cf132c6e999e002e1975c6ab7b",
        "city_id": link["city_id"],
        "district_id": "0",
        "token_name": "61bd10cf132c6e999e002e1975c6ab7b",
    }
    res = session.post(detail_url, headers=header1, data=data).json()
    return link, res


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


def fetch_data():
    res = session.get(base_url, headers=_headers).text
    locations = json.loads(
        res.split("var provine_name =")[1]
        .split("var")[0]
        .replace("\r\n", "")
        .strip()[:-1]
    )
    links = []
    for key, loc in locations.items():
        links.append(loc)
    logger.info(f"{len(links)} found")
    for link, res in fetchConcurrentList(links):
        for key, _ in enumerate(bs(res["html"], "lxml").select("li.find_store_item")):
            store_number = _["onclick"].split("(")[1].split(",")[0]
            raw_address = _.select_one("div.store_name p").text.strip()
            addr = parse_address_intl(raw_address + ", Vietnam")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            coord = res["restaurant"][key]
            latitude = coord[1]
            longitude = coord[2]
            if float(latitude) < -90 or float(latitude) > 90:
                latitude = str(latitude)[:2] + "." + str(latitude)[2:]
            if float(longitude) < -180 or float(longitude) > 180:
                longitude = str(longitude)[:3] + "." + str(longitude)[3:]

            hours = list(_.select_one("div.find_store_des").stripped_strings)[1:]
            yield SgRecord(
                page_url=res["url"],
                store_number=store_number,
                location_name=_.select_one("div.store_name h5")
                .text.replace("–", "-")
                .strip(),
                street_address=street_address,
                city=link["name"],
                state=addr.state,
                country_code="Vietnam",
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

        session.close()
