from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://www.megaplextheatres.com/"
base_url = "https://apiv2.megaplextheatres.com/api/cinema/cinemas"


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        locations = session.get(base_url).json()
        for _ in locations:
            page_url = locator_domain + _["name"].lower().replace(" ", "")
            addr = _["address2"].strip().split(",")
            raw_address = _["address1"] + " " + _["address2"]
            state = addr[1].strip().split()[0]
            if state.isdigit():
                state = ""
            zip_postal = addr[1].strip().split()[-1]
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address1"],
                city=addr[0].strip(),
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                latitude=_["latitude"],
                longitude=_["longitude"],
                phone=_["phoneNumber"],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
