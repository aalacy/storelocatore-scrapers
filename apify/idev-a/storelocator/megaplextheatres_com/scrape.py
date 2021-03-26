from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

locator_domain = "https://www.megaplextheatres.com/"
base_url = "https://www.megaplextheatres.com/api/theatres/all"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url).json()
        for _ in locations:
            page_url = locator_domain + _["name"].lower().replace(" ", "")
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code="US",
                latitude=_["latitude"],
                longitude=_["longitude"],
                phone=_["phone"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
