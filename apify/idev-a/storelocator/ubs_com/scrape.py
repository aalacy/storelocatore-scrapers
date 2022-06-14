from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.ubs.com"
base_url = "https://www.ubs.com/locations/_jcr_content.lofisearch.all.en.data"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["hits"]["hits"]
        for info in locations:
            _ = info["fields"]
            raw_address = _["bu_localizedFullAddress"][1]
            addr = parse_address_intl(raw_address + ", " + _["country"][0])
            page_url = "https://www.ubs.com/locations.html#switzerland" + _["id"][0]
            try:
                latitude = _["latitude"][0]
                longitude = _["longitude"][1]
            except:
                latitude = longitude = ""

            street_address = raw_address.split(",")[0]
            if (
                street_address.isdigit()
                or street_address.endswith("/F")
                or street_address.endswith("Floor")
            ):
                street_address += " " + raw_address.split(",")[1]

            yield SgRecord(
                page_url=page_url,
                store_number=info["number"],
                location_name=_["title"][0],
                street_address=street_address,
                city=_["bu_city"][0],
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=latitude,
                longitude=longitude,
                country_code=_["country"][0],
                location_type=_["pod_locationType"][0],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
