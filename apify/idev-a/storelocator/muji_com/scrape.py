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
        hours.append(hh.split("）")[-1].replace("～", "-").replace("~", "-"))

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
            raw_address = (
                _["shopaddress"]
                .replace("（", "(")
                .replace("）", ")")
                .replace("，", ",")
                .replace(".", ". ")
            )
            if (
                "Tokyo" in raw_address
                or "Kanagawa" in raw_address
                or "Kyoto" in raw_address
                or "Osaka" in raw_address
                or "Fukuoka" in raw_address
                or "Aichi" in raw_address
                or "Fujisawa" in raw_address
            ):
                country_code = "JP"
            _addr = raw_address
            if country_code:
                _addr += ", " + country_code
            addr = parse_address_intl(_addr)
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if country_code == "JP":
                street_address = " ".join(raw_address.split(",")[:-1])
            else:
                if street_address.replace("-", "").isdigit():
                    street_address = raw_address.split(",")[0].strip()
            phone = _["tel"].replace("\u3000", "").strip()
            if phone:
                phone = phone.split(" ")[0]
            if phone == "-":
                phone = ""
            city = addr.city or ""
            if (
                city
                or ("city" in raw_address.lower() and "city" not in city.lower())
                or city.lower() == "city"
            ):
                rr = raw_address.split(",")
                if len(rr) > 1:
                    for aa in rr:
                        if "city" in aa.lower():
                            _city = []
                            dd = aa.split("#")[0].strip().split(" ")
                            if dd[-1].strip().isdigit():
                                del dd[-1]
                            for cc in dd[-2:]:
                                if not cc.strip().isdigit():
                                    _city.append(cc)
                            city = " ".join(_city)
                            break
                city = city.split("#")[0]
                if street_address == "1F" or (
                    city and street_address.replace("-", "").isdigit()
                ):
                    x = raw_address.find(city)
                    street_address = raw_address[:x].replace(",", " ").strip()

            yield SgRecord(
                location_name=_["shopname"],
                store_number=_["shopid"],
                street_address=street_address.replace("Shaoxing", "").replace(
                    "Zhenjiang", ""
                ),
                city=city.replace("Ilsandong-Gu", "")
                .replace("Ilsandong-Gu", "")
                .replace("Giheung-Gu", "")
                .replace("Danwon-Gu", "")
                .replace("Suji-Gu", "")
                .replace("  Fujisawa-shi", ""),
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                latitude=_["latitude"],
                longitude=_["longitude"],
                hours_of_operation=_h(_["opentime"]),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
