from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pfchangs")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = ""
base_urls = [
    "http://www.pfchangs.cr/ubicaciones.html",
    "http://www.pfchangs.gt/ubicaciones.html",
    "http://www.pfchangs.com.pa/ubicaciones.html",
]

countries = ["Costa Rica", "Guatemala", "Panama"]


def _coord(locs, name):
    lat = lng = ""
    for loc in locs:
        if name in loc.p.text:
            lat = loc.iframe["src"].split("&lat=")[1].split("&")[0]
            lng = loc.iframe["src"].split("&lon=")[1].split("&")[0]

    return lat, lng


def fetch_data():
    with SgRequests() as session:
        for x, url in enumerate(base_urls):
            sp1 = bs(session.get(url, headers=_headers).text, "lxml")
            locations = sp1.select("section#location div.row > div")
            logger.info(f"{url} {len(locations)} found")
            locs = sp1.select("div.zerogrid div.item-container")
            for _ in locations:
                p = _.select("p")
                raw_address = list(p[2].stripped_strings)[-1]
                addr = parse_address_intl(raw_address + f", {countries[x]}")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                phone = ""
                _pp = list(p[0].stripped_strings)
                if len(_pp) > 1:
                    phone = _pp[-1]
                hours = ""
                _hr = list(p[3].stripped_strings)
                if _hr:
                    hours = _hr[-1]
                lat, lng = _coord(locs, _.h2.text.strip())
                yield SgRecord(
                    page_url=url,
                    location_name=_.h2.text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code=countries[x],
                    phone=phone,
                    latitude=lat,
                    longitude=lng,
                    locator_domain=locator_domain,
                    hours_of_operation=hours.replace("|", ";"),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
