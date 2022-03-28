from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("perfectpizza")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.perfectpizza.co.uk/"
base_url = "https://www.perfectpizza.co.uk/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("select#shopShortName option")
        for option in locations:
            if not option.get("value"):
                continue
            page_url = (
                f"https://www.perfectpizza.co.uk/?postcode=&shortname={option['value']}"
            )
            res = session.get(page_url, headers=_headers)
            sp1 = bs(res.text, "lxml")
            addr = list(sp1.select_one("div.address p").stripped_strings)
            hours = []
            for hh in list(sp1.select_one("div.open").stripped_strings)[1:]:
                if "note" in hh or "contact" in hh:
                    break
                if "notice" in hh or "store" in hh or "delivery" in hh:
                    continue
                hours.append(hh)
            phone = addr[-1]
            if phone == ".":
                phone = ""
            yield SgRecord(
                page_url=res.url,
                location_name=sp1.select_one("h2.pageTitle").text.strip(),
                street_address=addr[0],
                city=" ".join(addr[1].split(" ")[:-2]),
                zip_postal=" ".join(addr[1].split(" ")[-2:]),
                country_code="UK",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("\xa0", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
