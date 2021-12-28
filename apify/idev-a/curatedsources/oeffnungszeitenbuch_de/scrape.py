from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.oeffnungszeitenbuch.de"
base_url = "https://www.oeffnungszeitenbuch.de/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        cities = soup.select("div#textbereich > table a")
        for city in cities:
            city_base = city["href"]
            logger.info(city_base)
            pages = bs(session.get(city_base, headers=_headers).text, "lxml").select(
                "select#seitennr option"
            )
            for page in pages:
                section_url = city_base.split("-")[0] + "-" + page.text + ".html"
                logger.info(section_url)
                links = bs(
                    session.get(section_url, headers=_headers).text, "lxml"
                ).select("div.cboxserp")
                for link in links:
                    page_url = link.a["href"]
                    logger.info(page_url)
                    sp2 = bs(session.get(page_url, headers=_headers).text, "lxml")
                    addr = list(
                        sp2.select("span.entryAdrFnt > div")[1].stripped_strings
                    )[:3]
                    phone = ""
                    if sp2.select_one("span.telClk"):
                        phone = sp2.select_one("span.telClk").text.strip()
                    hours = []
                    for hh in sp2.select("table.zeitenTbl tr"):
                        td = hh.select("td")
                        if len(td) == 1:
                            break
                        hours.append(" ".join(hh.stripped_strings))

                    yield SgRecord(
                        page_url=page_url,
                        location_name=link.a.text.strip(),
                        street_address=addr[0],
                        city=addr[-1],
                        zip_postal=addr[1],
                        country_code="DE",
                        phone=phone,
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                        raw_address=" ".join(addr),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
