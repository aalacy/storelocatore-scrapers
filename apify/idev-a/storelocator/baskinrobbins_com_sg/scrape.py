from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("baskinrobbins")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://baskinrobbins.com.sg"
base_url = "https://baskinrobbins.com.sg/content/baskinrobbins/en/location.html"


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            soup = bs(session.get(base_url, headers=_headers).text, "lxml")
            locations = soup.select("ul#myUL li a")
            for _ in locations:
                raw_address = (
                    _.h5.find_next_sibling("p")
                    .text.replace("\n", " ")
                    .replace("\r", "")
                    .strip()
                )
                addr = raw_address.split(",")
                name = list(_.h5.stripped_strings)
                _p = list(_.select_one("p.availability").stripped_strings)
                if "Tel" not in _p[0]:
                    del _p[0]
                phone = _p[1]
                if phone == "N/A":
                    phone = ""
                map_url = _["onclick"].split("location.href=")[1][1:-2]
                logger.info(map_url)
                driver.get(map_url)
                driver.wait_for_request("/@", timeout=15)
                coord = driver.current_url.split("/@")[1].split("/data")[0].split(",")
                yield SgRecord(
                    page_url=base_url,
                    location_name=name[0],
                    street_address=" ".join(addr[:-2]),
                    city=addr[-2].strip(),
                    zip_postal=addr[-1].strip(),
                    country_code="SG",
                    phone=phone,
                    latitude=coord[0],
                    longitude=coord[1],
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.PHONE, SgRecord.Headers.CITY}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
