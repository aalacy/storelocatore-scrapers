from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.texaschickenandburgers.com/"
    base_url = "https://www.texaschickenandburgers.com/get-markers"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["data"]:
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            page_url = locator_domain + _["url"]
            hours = []
            if len(_["hours"]) == 1:
                hours += [f"Monday-Sunday: {_['hours'][0]}"]
            if len(_["hours"]) == 2 or len(_["hours"]) == 3:
                hours += [f"Sunday-Thursday: {_['hours'][0]}"]
                hours += [f"Friday-Saturday: {_['hours'][1]}"]

            yield SgRecord(
                page_url=page_url,
                raw_address=_["address"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                latitude=_["lat"],
                longitude=_["long"],
                zip_postal=addr.postcode,
                country_code="US",
                phone=_["phone"].replace("TBD", "").split("Drive")[0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
