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

locator_domain = "https://www.al-baik.in"
base_url = "https://www.al-baik.in/restaurants"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.col-md-4.mb-md-4.mb-3")
        for _ in locations:
            page_url = locator_domain + _.a["href"]
            raw_address = (
                " ".join(list(_.p.stripped_strings)[1:])
                .replace("\t", " ")
                .replace("\n", "")
                .replace("\r", "")
                .replace("  ", "")
            )
            addr = parse_address_intl(raw_address + ", India")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = list(_.select("p")[1].stripped_strings)[1]
            if hours == "-":
                hours = ""
            zip_postal = addr.postcode
            if zip_postal:
                temp = [tt for tt in zip_postal if tt.isdigit()]
                zip_postal = "".join(temp)
            country_code = addr.country
            if "Nepal" in country_code:
                country_code = "Nepal"
            yield SgRecord(
                page_url=page_url,
                location_name="",
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_postal,
                country_code=country_code,
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
