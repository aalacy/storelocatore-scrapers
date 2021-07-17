from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.sbe.com"
base_url = "https://www.sbe.com/mapdata.json"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for loc in locations:
            for cluster in loc["clusters"]:
                for _ in cluster["types"]["hotel"]:
                    yield SgRecord(
                        page_url=_["link"],
                        store_number=_["id"],
                        location_name=_["name"].split("(")[0],
                        street_address=_["address"]["street"],
                        city=_["address"]["city"],
                        state=_["address"]["state"],
                        zip_postal=_["address"]["postal"],
                        latitude=_["coordinates"]["lat"],
                        longitude=_["coordinates"]["lng"],
                        phone=_["phone"],
                        locator_domain=locator_domain,
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
