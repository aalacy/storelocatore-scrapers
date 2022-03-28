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

locator_domain = "https://www.modainpelle.com"
base_url = "https://www.modainpelle.com/map"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.store-locator__store")
        for _ in locations:
            page_url = (
                locator_domain + _.select_one("a.store-locator__store__href")["href"]
            )

            addr = list(
                _.select_one("div.store-locator__store__info_left p").stripped_strings
            )
            phone = _.select("div.store-locator__store__info_left span")[
                -1
            ].text.strip()
            hours = _.select_one(
                "div.store-locator__store__info_right"
            ).stripped_strings
            city = addr[-3].strip()
            state = addr[-2].strip()
            s_idx = -3
            if "Street" in city:
                s_idx += 1
                city = state
                state = ""
            street_address = " ".join(addr[:s_idx])
            logger.info(page_url)
            res = session.get(base_url, headers=_headers).text
            coord = res.split("google.maps.LatLng(")[1].split(")")[0].split(",")
            yield SgRecord(
                page_url=page_url,
                location_name=_.select_one(
                    "strong.store-locator__store__title"
                ).text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=addr[-1].strip(),
                country_code="UK",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
