from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.toolstation.com"
base_url = "https://www.toolstation.com/branches"
max_workers = 16


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


def fetchConcurrentSingle(link):
    page_url = link["href"]
    response = request_with_retries(page_url)
    if response.status_code == 200:
        return page_url, response.text, bs(response.text, "lxml")


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
    with SgRequests(proxy_country="us") as session:
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "ul.branches-ul > li a"
        )
        for page_url, res, sp1 in fetchConcurrentList(locations):
            logger.info(page_url)
            _ = json.loads(res.split("var store =")[1].split("</script>")[0].strip())[0]
            bb = list(bs(_["address_text"], "lxml").stripped_strings)
            raw_address = bb[0]
            addr = raw_address.split(",")
            phone = ""
            if sp1.select_one('a[itemprop="telephone"]'):
                phone = sp1.select_one('a[itemprop="telephone"]').text.strip()

            hours = []
            if len(bb) > 1:
                for hh in bb[1].split(","):
                    day = hh.split(":")[0].strip()
                    times = hh.split(":")[-1].strip()
                    start = _time(times.split("-")[0].strip())
                    end = _time(times.split("-")[-1].strip())
                    hours.append(f"{day}: {start} - {end}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["site_id"],
                location_name=_["name"],
                street_address=", ".join(addr[:-2]),
                city=addr[-2],
                zip_postal=_["postcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
