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

locator_domain = "https://7-eleven.no"
base_url = "https://7-eleven.no/butikker"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.list ol li")
        for _ in locations:
            url = f"https://7-eleven.no/ajax/hours?store={_['data-storeid']}"
            hours = []
            _hr = []
            try:
                _hr = session.get(url, headers=_headers).json()
            except:
                pass
            for hh in _hr:
                hours.append(f"{hh['dagTekst']}: {hh['fra']} - {hh['til']}")
            yield SgRecord(
                page_url=base_url,
                store_number=_["data-storeid"],
                location_name=_["data-title"],
                street_address=_.select_one("div.street-address").text.strip(),
                city=_.select_one("span.locality").text,
                country_code="Norway",
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
