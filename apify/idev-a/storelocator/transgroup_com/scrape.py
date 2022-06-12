from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("transgroup")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.scangl.com"
base_url = "https://www.scangl.com/about/our-locations/"
url = "https://siws.transgroup.com/StationInfo.asmx/GetStationInfoJSonIncludeSpecServices?callback=jQuery183023879191175909176_1625502747472&cityCode=%22{}%22&_=1625502788447"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.accordion-country ul li")
        logger.info(f"{len(links)} found")
        for _ in links:
            page_url = locator_domain + _.select("a")[-1]["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            hours = []
            if res.status_code == 200:
                sp1 = bs(res.text, "lxml")
                hours = list(
                    sp1.select_one("div.office-time div.information p").stripped_strings
                )
                if hours:
                    hours = hours[1:]
            _addr = list(_.stripped_strings)[2:-2]
            if "Fax" in _addr[-1]:
                del _addr[-1]
            phone = ""
            if "Tel" in _addr[-1]:
                phone = _addr[-1].replace("Tel", "")
                del _addr[-1]
            addr = parse_address_intl(" ".join(_addr))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            yield SgRecord(
                page_url=page_url,
                location_name=_.strong.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                phone=phone,
                locator_domain=locator_domain,
                raw_address=" ".join(_addr),
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
