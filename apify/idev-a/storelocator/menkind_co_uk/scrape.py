from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.menkind.co.uk"
base_url = "https://www.menkind.co.uk/storelocator"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.storefinder-search-store")
        for _ in locations:
            raw_address = (
                _.select_one("div.storefinder-search-store-address")
                .text.replace("\n", "")
                .replace("\r", ",")
                .strip()
            )
            addr = parse_address_intl(raw_address + ", United Kingdom")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if not city:
                city = _.h2.text.replace("Menkind", "").strip()
            if street_address.strip() == "29A" or street_address.strip() == "Unit 87":
                street_address = ""
                for aa in raw_address.split(","):
                    if not aa.strip():
                        continue
                    if aa == city:
                        break
                    street_address += " " + aa
            phone = ""
            if _.select_one("div.storefinder-search-store-telephone-number"):
                phone = _.select_one(
                    "div.storefinder-search-store-telephone-number"
                ).text.strip()

            page_url = _.select_one("a.storefinder-search-store-link")["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            for hh in list(
                sp1.select_one("div.storefinder-data-opening-times").stripped_strings
            )[1:]:
                if "We are" in hh or "For more" in hh:
                    break
                hours.append(hh)

            yield SgRecord(
                page_url=page_url,
                location_name=_.h2.text.strip(),
                street_address=street_address.strip(),
                city=city.replace("Street", ""),
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="UK",
                phone=phone,
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
