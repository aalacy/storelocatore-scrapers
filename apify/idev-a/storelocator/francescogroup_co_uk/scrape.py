from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("francescogroup")

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://www.francescogroup.co.uk/salons/find-a-salon/",
    "origin": "https://www.francescogroup.co.uk",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://www.francescogroup.co.uk/salons/find-a-salon/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.francescogroup.co.uk"
base_url = "https://www.francescogroup.co.uk/wp-admin/admin-ajax.php"


def fetch_data():
    with SgRequests() as session:
        data = "action=store_wpress_listener&method=display_map&page_number=1&lat=52.6043062&lng=-1.9176463&category_id=&max_distance=&nb_display=45"
        locations = session.post(base_url, headers=_headers, data=data).json()[
            "locations"
        ]
        for _ in locations:
            page_url = _["url"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=header1).text, "lxml")
            _hr = sp1.find("h3", string=re.compile(r"When We(.)re Open", re.I))
            hours = []
            if _hr and _hr.find_next_sibling("div"):
                days = list(_hr.find_next_sibling("div").p.stripped_strings)
                times = list(
                    _hr.find_next_sibling("div")
                    .select_one("p.opening_hours_iq")
                    .stripped_strings
                )
                for x in range(len(days)):
                    hours.append(f"{days[x]}: {times[x]}")
            elif sp1.select_one("table.hours_table"):
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in sp1.select("table.hours_table tr")
                ]
            try:
                street_address = sp1.select_one(
                    'span[itemprop="streetAddress"]'
                ).text.strip()
                city = sp1.select_one('span[itemprop="addressLocality"]').text.strip()
                state = sp1.select_one('span[itemprop="addressRegion"]').text.strip()
                zip_postal = sp1.select_one('span[itemprop="postalCode"]').text.strip()
                raw_address = sp1.select_one('div[itemprop="address"]').text.strip()
            except:
                raw_address = _["address"]
                addr = raw_address.split(",")
                street_address = ", ".join(addr[:-2])
                city = addr[-2]
                zip_postal = addr[-1]
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="UK",
                phone=_["tel"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("for bookings", ""),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
