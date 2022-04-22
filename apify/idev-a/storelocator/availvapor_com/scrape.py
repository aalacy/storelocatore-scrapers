from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("availvapor")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://availvapor.com"
base_url = "https://availvapor.com/index.php?hcs=locatoraid&hcrand=3602&hca=search%3Asearch%2F%2Fproduct%2F_PRODUCT_%2Flat%2F%2Flng%2F%2Flimit%2F1000"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["results"]
        for loc in locations:
            page_url = bs(loc["misc7"], "lxml").a["href"]
            logger.info(page_url)
            url = bs(session.get(page_url, headers=_headers).text, "lxml").select_one(
                "form.hclc_search_form_class"
            )["action"]
            _ = session.get(url, headers=_headers).json()["results"][0]
            raw_address = " ".join(bs(_["address"], "lxml").stripped_strings)
            street_address = _["street1"]
            if _["street2"]:
                street_address += " " + _["street2"]
            hours = []
            hours.append(f"Monday - Thursday: {_['misc1']} - {_['misc2']}")
            hours.append(f"Saturaday: {_['misc3']} - {_['misc4']}")
            hours.append(f"Sunday: {_['misc5']} - {_['misc6']}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address.replace("&#039;", "'"),
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=bs(_["phone"], "lxml").text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
