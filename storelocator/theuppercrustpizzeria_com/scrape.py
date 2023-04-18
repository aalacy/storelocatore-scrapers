from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("theuppercrustpizzeria")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.theuppercrustpizzeria.com"
base_url = "https://www.theuppercrustpizzeria.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = base_url + "#" + link["id"]
            block = list(link.p.stripped_strings)
            block_inf = " ".join(block)
            location_type = ""
            if "COMING SOON" in block_inf:
                location_type = "COMING SOON"
            addr = block[0].split(",")
            if len(block) > 2:
                addr = block[1].split(",")
            sub_addr = " ".join(addr[1:]).strip()
            sub_addr = " ".join(sub_addr.split())
            phone = ""
            if len(block) > 1:
                phone = block[1].split("at")[-1]
            if len(block) > 2:
                phone = block[2].split("at")[-1]

            yield SgRecord(
                page_url=page_url,
                location_name=link.strong.text.strip(),
                street_address=addr[0].replace("We are on", "").strip(),
                city=" ".join(sub_addr.split()[:-2]),
                state=sub_addr.split()[-2].strip(),
                zip_postal=sub_addr.split()[-1].strip(),
                country_code="US",
                phone=phone,
                location_type=location_type,
                locator_domain=locator_domain,
                raw_address=addr[0].replace("We are on", "").strip() + " " + sub_addr,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
