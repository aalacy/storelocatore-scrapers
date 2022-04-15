from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.discovervision.com/locations/"
locator_domain = "https://www.discovervision.com/"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.cpt-location-info"
        )
        for _ in locations:
            addr = list(_.p.stripped_strings)
            street_address = " ".join(addr[:-1])
            if street_address.endswith(","):
                street_address = street_address[:-1]
            coord = (
                _.iframe["src"]
                .split("!2d")[1]
                .split("!2m")[0]
                .split("!3m")[0]
                .split("!3d")
            )
            hours = []
            for hh in list(_.h2.find_next_sibling().stripped_strings):
                if "*" in hh:
                    continue
                hours.append(hh)
            yield SgRecord(
                page_url=_.find_previous_sibling()["href"],
                location_name=_.find_previous_sibling().text.strip(),
                street_address=street_address,
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                phone=list(_.select_one("ul.location-phone-list li").stripped_strings)[
                    -1
                ],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
