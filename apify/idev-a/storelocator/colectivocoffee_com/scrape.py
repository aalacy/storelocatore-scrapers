from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("colectivocoffee")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://colectivocoffee.com"
    base_url = "https://colectivocoffee.com/cafes"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select('div.w-dyn-list div[role="listitem"]')
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _addr = sp1.select_one("div.cafe-details-list-item").text.strip()
            addr = parse_address_intl(_addr)
            street_address = _addr.split(",")[0].replace(addr.city, "")
            hours = []
            temp = []
            for hh in sp1.select_one("div.cafe-hours").stripped_strings:
                if (
                    "Offering" in hh
                    or "Indoor" in hh
                    or "Ordering" in hh
                    or "Christmas" in hh
                ):
                    break
                temp.append(hh.replace("Â\xa0", " ").replace("â\x80\x93", "-"))
            temp = [hh for hh in temp if hh != "â\x80\x8d" and hh != "\u200d"]
            if temp:
                try:
                    for x in range(0, len(temp), 2):
                        hours.append(f"{temp[x]}: {temp[x+1]}")
                except:
                    import pdb

                    pdb.set_trace()
            else:
                hours = temp
            yield SgRecord(
                page_url=page_url,
                location_name=link.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=sp1.select("div.cafe-details-list-item")[1].text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=_addr,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
