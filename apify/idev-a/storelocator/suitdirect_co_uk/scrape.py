from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal.sgpostal import parse_address_intl


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.suitdirect.co.uk"
base_url = "https://www.suitdirect.co.uk/store-locator/"


def get_loc(locations, name):
    for _ in locations:
        if _["name"] == name:
            return _

    return {}


def fetch_data():
    with SgRequests() as session:
        sp1 = bs(session.get(base_url, headers=_headers).text, "lxml")
        locs = sp1.select("div.storeAddress")
        locations = json.loads(
            sp1.select_one('script[type="application/ld+json"]').string
        )
        for loc in locs:
            try:
                name = loc.h5.text.strip()
            except:
                continue
            if "Coming Soon" in name:
                continue
            _ = get_loc(locations, name)
            addr = _["address"][0]
            hours = []
            for hh in loc.select("div.storeTimes li"):
                hours.append(": ".join(hh.stripped_strings))

            city = addr["addressLocality"]
            if not city and name not in ["Dalton Park"]:
                city = name

            if not city:
                aa = parse_address_intl(addr["name"] + ", United Kingdom")
                if aa.city:
                    city = aa.city

            page_url = locator_domain + loc.a["href"]
            street_address = loc.select_one("span.storeSingleLine").text.strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            _addr = street_address.split(",")
            if city and city == _addr[-1].strip():
                del _addr[-1]
            street_address = ", ".join(_addr)
            yield SgRecord(
                page_url=page_url,
                location_name=name,
                street_address=street_address,
                city=city,
                zip_postal=addr["postalCode"],
                latitude=loc.select_one("span.storeAddressData")["data-storelatitude"],
                longitude=loc.select_one("span.storeAddressData")[
                    "data-storelongitude"
                ],
                country_code="UK",
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=addr["name"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
