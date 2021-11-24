from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl
import re
import us

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("cellairis")

_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.cellairis.com"
base_url = "https://www.cellairis.com/store-locator-data-all.json?origLat=34.1116052&origLng=-84.2120597&origAddress=4Q6Q%2BJ5%20Alpharetta%2C%20GA%2C%20USA&formattedAddress=&boundsNorthEast=&boundsSouthWest="
urls = [
    "https://www.cellairis.com/stores/d.f.-santa-fe-mall-iphone-repair",
    "https://www.cellairis.com/stores/ciudad-de-mexico-telefono-celular-iphone-reparacion",
]


def get_country_by_code(code=""):
    if us.states.lookup(code):
        return "US"
    else:
        return "MX"


def fetch_one(http):
    for page_url in urls:
        sp1 = bs(http.get(page_url, headers=_headers).text, "lxml")
        raw_address = " ".join(sp1.select_one("div.promoDesc p").stripped_strings)
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = ""
        if sp1.find("a", href=re.compile(r"tel:")):
            phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
        days = [dd.text.strip() for dd in sp1.select("p.storeHours span.storedays")]
        times = [tt.text.strip() for tt in sp1.select("p.storeHours span.storetime")]
        hours = []
        for x in range(len(times)):
            hours.append(f"{days[x]} {times[x]}")
        coord = sp1.iframe["src"].split("&center=")[1].split(",")
        yield SgRecord(
            page_url=page_url,
            location_name="Cellairis",
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            latitude=coord[0],
            longitude=coord[1],
            country_code="MX",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
            raw_address=raw_address,
        )


def fetch_records(http):
    locations = http.get(base_url, headers=_headers).json()
    for _ in locations:
        page_url = f"https://www.cellairis.com/stores/{_['HomePage']}"
        zip_postal = _.get("postal")
        country_code = _["CountryCode"]
        if zip_postal == "US":
            country_code, zip_postal = zip_postal, country_code
        if not country_code:
            country_code = get_country_by_code(_.get("state"))
        yield SgRecord(
            page_url=page_url,
            location_name=_["name"],
            street_address=_["address"],
            city=_["city"],
            state=_.get("state"),
            zip_postal=zip_postal,
            latitude=_["lat"],
            longitude=_["lng"],
            country_code=country_code,
            phone=_["phone"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(bs(_["hours1"], "lxml").stripped_strings),
        )


if __name__ == "__main__":
    with SgRequests() as http:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            for rec in fetch_one(http):
                writer.write_row(rec)

            for rec in fetch_records(http):
                writer.write_row(rec)
