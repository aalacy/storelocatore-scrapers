from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.iconcinemas.com"
base_url = "https://www.iconcinemas.com/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.feature a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            alert = sp1.select_one("div#alertMessage img.img-responsive")
            if alert and "edmondcomingsoonart.jpg" in alert["src"]:
                continue
            addr = list(sp1.select_one("div#footer-address p a").stripped_strings)
            map_url = page_url + sp1.select_one("div#footer-address p a")["href"]
            res = session.get(map_url, headers=_headers).text
            try:
                coord = (
                    res.split("new google.maps.LatLng(")[1].split(");")[0].split(",")
                )
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h2.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1]
                .replace("\xa0", " ")
                .split(",")[1]
                .strip()
                .split(" ")[-1]
                .strip(),
                country_code="US",
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
