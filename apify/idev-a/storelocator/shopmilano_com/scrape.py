from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://shopmilano.com"
base_url = "https://shopmilano.com/pages/our-locations"
json_url = "https://apps.elfsight.com/p/boot/?w={}"


def fetch_data():
    with SgRequests() as session:
        key = (
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("div.user-content div")["class"][0]
            .split("app-")[-1]
        )
        locations = session.get(json_url.format(key), headers=_headers).json()["data"][
            "widgets"
        ][key]["data"]["settings"]["markers"]
        for _ in locations:
            raw_address = _["position"].replace("St. Maarten", "Sint Maarten")
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            latlng = _["coordinates"].split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=_["infoTitle"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=latlng[0],
                longitude=latlng[1],
                country_code=addr.country,
                locator_domain=locator_domain,
                raw_address=_["position"],
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
