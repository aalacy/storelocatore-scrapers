from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("chevys")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.chevys.com/"
base_url = "https://www.chevys.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("#content section.content-module.locations div.location")
        for link in links:
            page_url = link.h2.a["href"]
            if "Coming Soon" in link.h2.a.text:
                continue
            logger.info(page_url)
            soup1 = bs(session.get(page_url).text, "lxml")
            try:
                direction = (
                    link.select_one("div.location-links a")["href"]
                    .split("destination=")[1]
                    .strip()
                    .split(",")
                )
            except:
                direction = (
                    soup1.select("div.location-contact p")[1]
                    .a["href"]
                    .split("destination=")[1]
                    .strip()
                    .split(",")
                )
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in soup1.select("div.location-hours div.hours div.hours--detail")
            ]
            address = list(soup1.select_one("div.location-address a").stripped_strings)
            yield SgRecord(
                page_url=page_url,
                store_number=link["data-location-id"],
                location_name=link.h2.a.text.strip(),
                street_address=address[0],
                city=address[1].split(",")[0],
                state=address[1].split(",")[1].strip(),
                country_code="US",
                latitude=direction[0],
                longitude=direction[1],
                phone=soup1.select_one("div.location-contact p a").text,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(address),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
