from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://thecoop.ca/"
    base_url = "https://thecoop.ca/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.single-page-content div.wpex-vc_section-has-fill")
        for _ in locations:
            addr = list(_.select("p")[0].stripped_strings)
            hours = list(_.select("p")[1].stripped_strings)
            try:
                coord = _.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            except:
                coord = ("", "")
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=addr[0].replace(",", ""),
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0],
                zip_postal=" ".join(addr[1].split(",")[1].strip().split(" ")[1:]),
                country_code="CA",
                phone=addr[2],
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("—", "-").replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
