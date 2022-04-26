from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.essaroil.co.uk"
base_url = "https://www.essaroil.co.uk/our-forecourts/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.main div.section-box")
        for link in locations:
            page_url = locator_domain + link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = []
            for aa in list(sp1.h1.find_next_sibling().p.stripped_strings):
                addr += [dd.strip() for dd in aa.split(",") if dd.strip()]

            if "Directions" in addr[-1]:
                del addr[-1]

            phone = ""
            hours = ""
            for p in sp1.h1.find_next_sibling().select("p"):
                _p = p.text.strip()
                if not _p:
                    continue
                if "Telephone" in _p:
                    phone = _p.split(":")[-1]
                if "Opening times" in _p:
                    hours = (
                        _p.replace("Opening times:", "")
                        .replace("and", "; ")
                        .split("Telephone")[0]
                    )
                    if not hours:
                        hours = "; ".join(p.find_next_sibling().stripped_strings)

            coord = (
                sp1.h1.find_next_sibling()
                .a["href"]
                .split("/@")[1]
                .split("/data")[0]
                .split(",")
            )

            zip_postal = addr[-1].replace(",", "").strip()

            c_i = -3
            state = ""
            if len(addr) == 3:
                c_i += 1
            else:
                state = addr[-2].replace(",", "").strip()
            city = addr[c_i].replace(",", "").strip()
            street_address = " ".join(addr[:c_i])

            if street_address.endswith(","):
                street_address = street_address[:-1]
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h1.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal.replace("\xa0", "").strip(),
                country_code="UK",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=", ".join(addr).replace("\xa0", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
