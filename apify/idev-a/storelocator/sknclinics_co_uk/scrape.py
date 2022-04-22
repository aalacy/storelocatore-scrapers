from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
import re

logger = SgLogSetup().get_logger("sknclinics")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.sknclinics.co.uk"
base_url = "https://www.sknclinics.co.uk/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMrQ0ilHSAQkVZ5QWeLoUA0WjY4ECyaXFJfm5bpmpOSkQsVqlWgAoVxcl"


def parse_addr(raw_address):
    if not raw_address.lower().endswith("uk") and "United Kingdom" not in raw_address:
        raw_address += ", United Kingdom"
    zip_postal = raw_address.split(",")[-2]
    addr = parse_address_intl(raw_address)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    city = addr.city
    if city and city.lower() in zip_postal.lower():
        zip_postal = zip_postal.replace(city, "").strip()
    if "2Fa" and "Westminster" in raw_address:
        city = "Westminster"
    state = addr.state
    zip_postal = zip_postal.split("(")[0].replace("Tunbridge Wells", "").strip()

    return street_address, city, state, zip_postal


def fetch_records(http):
    markders = http.get(base_url, headers=_headers).json()["markers"]
    for _ in markders:
        url = _["link"]
        if not url.startswith("http"):
            url = locator_domain + url
        logger.info(url)
        if _["description"]:
            _addr = list(bs(_["description"], "lxml").stripped_strings)
        else:
            _addr = list(bs(_["address"], "lxml").stripped_strings)

        if len(_addr) == 1:
            _addr = _addr[0].split("\n")
        new_addr = []
        for aa in _addr:
            if aa.endswith(","):
                aa = aa[:-1]
            new_addr.append(aa)
        raw_address = ", ".join(new_addr)
        street_address, city, state, zip_postal = parse_addr(raw_address)
        res = http.get(url, headers=_headers)
        phone = ""
        hours = []
        if res and res.status_code == 200:
            sp1 = bs(res.text, "lxml")
            try:
                if not street_address or not city or not zip_postal:
                    if sp1.select_one("div.hero-image-002__content p"):
                        raw_address = (
                            " ".join(
                                sp1.select_one(
                                    "div.hero-image-002__content p"
                                ).stripped_strings
                            )
                            + ", United Kingdom"
                        )
                        street_address, city, state, zip_postal = parse_addr(
                            raw_address
                        )
            except:
                pass
            if sp1.select("div.map-times-001__times div.map-times-001__time-row"):
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in sp1.select(
                        "div.map-times-001__times div.map-times-001__time-row"
                    )
                ]
            try:
                phone = sp1.select_one("a.map-times-001__link").text.strip()
            except:
                if sp1.main:
                    pp = sp1.main.find("a", href=re.compile(r"tel:"))
                    if pp:
                        phone = pp.text.strip()

        yield SgRecord(
            page_url=url,
            store_number=_["id"],
            location_name=_["title"],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code="UK",
            phone=phone,
            latitude=_["lat"],
            longitude=_["lng"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
            raw_address=raw_address,
        )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http):
                writer.write_row(rec)
