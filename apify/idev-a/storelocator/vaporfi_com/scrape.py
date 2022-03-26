from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("vaporfi")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.vaporfi.com"
base_url = "https://www.vaporfi.com/vape-shops/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.storeLocation")
        for _ in locations:
            country_code = _.select_one('div[itemprop="description"]').text.strip()
            if country_code not in ["Suriname", "Guatemala"]:
                country_code = "US"
            page_url = _.a["href"]
            logger.info(page_url)
            addr = " ".join(_.select_one('div[itemprop="address"]').stripped_strings)
            zip_postal = ""
            if _.select_one('span[itemprop="postalCode"]'):
                zip_postal = _.select_one('span[itemprop="postalCode"]').text.strip()
            hours = []
            coord = ["", ""]
            if not page_url.endswith("vape-shops/"):
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                hours = [
                    hh["content"] for hh in sp1.select('meta[itemprop="openingHours"]')
                ]
                try:
                    coord = (
                        sp1.select_one("a.store-map-link")["href"]
                        .split("/@")[1]
                        .split("/data")[0]
                        .split(",")
                    )
                except:
                    try:
                        coord = (
                            sp1.select_one("a.store-map-link")["href"]
                            .split("sll=")[1]
                            .split("&")[0]
                            .split(",")
                        )
                    except:
                        try:
                            coord = (
                                sp1.select_one("div.store-map iframe")["src"]
                                .split("!2d")[1]
                                .split("!3m")[0]
                                .split("!2m")[0]
                                .split("!3d")[::-1]
                            )
                        except:
                            pass
            yield SgRecord(
                page_url=page_url,
                location_name=_.select_one('div[itemprop="name"]').text.strip(),
                street_address=_.select_one(
                    'span[itemprop="streetAddress"]'
                ).text.strip(),
                city=_.select_one('span[itemprop="addressLocality"]').text.strip(),
                state=_.select_one('span[itemprop="addressRegion"]').text.strip(),
                zip_postal=zip_postal,
                country_code=country_code,
                phone=_.select_one('div[itemprop="telephone"]').text.strip(),
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=addr,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
