from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("uniurgentcare")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://uniurgentcare.com/"
    base_url = "https://uniurgentcare.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.module_row div.module_column")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            if not _.h1:
                continue
            page_url = _.h1.a["href"]
            logger.info(page_url)
            addr = list(_.select("p")[-2].stripped_strings)[1:]
            hours = _.select("p")[-1].stripped_strings
            try:
                coord = (
                    _.select("p")[-2]
                    .select("a")[-1]["href"]
                    .split("&sll=")[1]
                    .split("&")[0]
                    .split(",")
                )
            except:
                try:
                    coord = (
                        _.select("p")[-2]
                        .select("a")[-1]["href"]
                        .split("/@")[1]
                        .split("/data")[0]
                        .split(",")
                    )
                except:
                    coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=_.h1.a.text.strip().replace("–", "-"),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=_.h3.text.strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
