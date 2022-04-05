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

locator_domain = "https://www.smileys.de"
base_url = "https://www.smileys.de/bestellen/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        cities = soup.select("div.storeItem p a")
        for city in cities:
            city_url = city["href"]
            logger.info(city_url)
            _ = bs(session.get(city_url, headers=_headers).text, "lxml")
            block = list(_.select_one("h2.storeItem__address").stripped_strings)[1:]
            phone = block[-1]
            addr = block[:-1]
            if not addr:
                continue
            addr[-1] = addr[-1].replace(",", "")
            hours = list(_.select_one("div.storeItem__info__hours p").stripped_strings)
            yield SgRecord(
                page_url=city_url,
                location_name=_.strong.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].strip().split()[-1].strip(),
                zip_postal=addr[-1].strip().split()[0].strip(),
                country_code="Germany",
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
