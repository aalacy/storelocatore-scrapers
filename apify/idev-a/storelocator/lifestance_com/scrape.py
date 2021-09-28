from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("lifestance")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://lifestance.com/"
    base_url = "https://lifestance.com/location-sitemap.xml"
    with SgRequests(
        proxy_country="us", dont_retry_status_codes_exceptions=set([400, 403])
    ) as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "url loc"
        )
        logger.info(f"{len(locations)} locations found")
        total_cnt = 0
        for link in locations:
            page_url = link.text.strip()
            logger.info(f"{page_url}")
            response = session.get(page_url, headers=_headers)
            sp1 = bs(response.text, "lxml")
            location_name = sp1.select_one("h1.h1").text.strip()
            street_address = city = state = zip_postal = ""
            if sp1.select_one("div.self-center div.p"):
                total_cnt += 1
                logger.info(f"[{total_cnt}] in total")
                raw_address = " ".join(
                    sp1.select_one("div.self-center div.p").stripped_strings
                )
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                state = addr.state
                zip_postal = addr.postcode
            else:
                ln = location_name.split("–")
                raw_address = ln[-1].strip() + " " + ln[0].strip()
                street_address = ln[-1]
                city = ln[0].split(",")[0].strip()
                state = ln[0].split(",")[-1].strip()

            _hr = sp1.find("h2", string=re.compile(r"Hours Of Operation"))
            hours = []
            if _hr:
                hours = [
                    ":".join(hh.stripped_strings)
                    for hh in _hr.find_next_siblings("div")
                ]
            phone = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            try:
                coord = (
                    sp1.select_one("main figure a img")["src"]
                    .split("false%7C")[1]
                    .split(",+")
                )
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="UK",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
