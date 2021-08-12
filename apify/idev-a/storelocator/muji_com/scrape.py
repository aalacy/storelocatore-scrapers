from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("muji")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _h(val):
    _val = (
        val.replace("–", "-")
        .replace("\u3000", " ")
        .replace("Click & Meet:", "")
        .strip()
    )
    _hr = _val.split(",")
    hours = []
    for hh in _hr:
        if "holiday" in hh.lower():
            continue
        hours.append(hh)

    return "; ".join(hours)


def fetch_data():
    locator_domain = "https://www.muji.com/"
    base_url = "https://www.muji.com/storelocator/?_ACTION=_SEARCH&c=in&lang=EN&swLat=-87.59969385055629&swLng=-180&neLat=87.5996938505563&neLng=180"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            country_code = _["shopid"][:2]
            if country_code.isdigit():
                country_code = ""
            _addr = _["shopaddress"]
            if country_code:
                _addr += ", " + country_code
            addr = parse_address_intl(_addr)
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if country_code == "JP":
                street_address = " ".join(_["shopaddress"].split(",")[:-1])
            phone = _["tel"].replace("\u3000", "").strip()
            if phone:
                phone = phone.split(" ")[0]
            if phone == "-":
                phone = ""
            yield SgRecord(
                location_name=_["shopname"],
                store_number=_["shopid"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                latitude=_["latitude"],
                longitude=_["longitude"],
                hours_of_operation=_h(_["opentime"]),
                raw_address=_["shopaddress"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
