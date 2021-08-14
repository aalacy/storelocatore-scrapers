from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


logger = SgLogSetup().get_logger("circalighting")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.circalighting.com"
    base_url = "https://www.circalighting.com/showrooms/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.category-cms .pagebuilder-column")
        for _ in locations:
            if not _.select_one("div.more"):
                continue
            if "Coming Soon" in _.select_one("div.more").text:
                continue
            block = list(_.select_one("div.more").stripped_strings)
            if "Now Open" in block[1]:
                del block[1]
            page_url = locator_domain + _.select("div.more a")[-1]["href"]
            block = [
                bb
                for bb in block
                if bb != "MAKE APPOINTMENT"
                and "Opening" not in bb
                and "More Information" not in bb
            ]
            phone = ""
            if "Phone" in block[3]:
                phone = block[3].replace("Phone", "").strip()
            hours = []
            if len(block) >= 5:
                hours = block[4:]
            city_state = block[2].split(",")
            city = state = zip_postal = ""
            country = "US"
            if len(city_state) == 1:
                country = "UK"
                city = block[2].split(" ")[0].strip()
                zip_postal = " ".join(block[2].split(" ")[1:])
            else:
                city = city_state[0]
                state = city_state[1].strip().split(" ")[0].strip()
                zip_postal = city_state[1].strip().split(" ")[1].strip()
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            if sp1.select_one("div.gmap iframe"):
                try:
                    coord = (
                        sp1.select_one("div.gmap iframe")["src"]
                        .split("!2d")[1]
                        .split("!3m")[0]
                        .split("!2m")[0]
                        .split("!3d")
                    )
                except:
                    coord = (
                        sp1.select_one("div.gmap iframe")["src"]
                        .split("/@")[1]
                        .split("/data")[0]
                        .split(",")
                    )
            else:
                coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=block[0],
                street_address=block[1],
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country,
                phone=phone,
                latitude=coord[1],
                longitude=coord[0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
