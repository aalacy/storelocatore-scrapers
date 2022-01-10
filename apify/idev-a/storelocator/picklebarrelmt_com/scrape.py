from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://picklebarrelmt.com"
base_url = "https://picklebarrelmt.com/locations"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.location-background")
        for link in locations:
            page_url = link.find_parent("a")["href"]
            if "locations" not in page_url:
                continue
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            hours = []
            for hh in sp1.select_one("h4.LocationSub").find_next_siblings():
                if hh.name == "h4":
                    break
                hours.append(hh.text.strip())
            phone = ""
            if (
                sp1.select("h4.LocationSub")[-1].text == "Phone"
                and sp1.select("h4.LocationSub")[-1].find_next_sibling()
            ):
                phone = (
                    sp1.select("h4.LocationSub")[-1].find_next_sibling().text.strip()
                )
            raw_address = sp1.select_one("h4.Address").text.strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            latitude = res.split("var lat =")[1].split(";")[0].strip()[1:-1]
            longitude = res.split("var lng =")[1].split(";")[0].strip()[1:-1]
            yield SgRecord(
                page_url=page_url,
                location_name=link.h4.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
