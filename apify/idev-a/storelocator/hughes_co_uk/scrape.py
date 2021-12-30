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

locator_domain = "https://www.hughes.co.uk"
base_url = "https://www.hughes.co.uk/storefinder"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        options = soup.select("select.select--town option")
        for option in options:
            if not option.get("value"):
                continue
            page_url = option["data-redirect-url"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _addr = sp1.select_one("div.dig-pub--text h2").text.strip().split(",")
            city = _addr[-1].strip()
            if city.endswith("Centre"):
                city = sp1.select_one("div.dig-pub--text h1").text.strip()
            raw_address = sp1.select_one("div.address").text.strip()
            addr = raw_address.split(",")
            state = ""
            idx = -2
            if addr[-2].replace(".", "").lower().strip() != city.lower():
                state = addr[-2]
                idx -= 1
            street_address = ", ".join(addr[:idx]).replace("The Two Bears,", "").strip()
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div.col-hours table tbody tr")
            ]
            coord = (
                sp1.select("div.box--content a.navigation--link")[-1]["href"]
                .split("/")[-1]
                .split(",")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=option.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=addr[-1].strip(),
                country_code="UK",
                phone=sp1.select_one(
                    "div.box--content a.navigation--link"
                ).text.strip(),
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
