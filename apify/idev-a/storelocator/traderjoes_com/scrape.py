from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("traderjoes")


def _headers(referer="https://locations.traderjoes.com/"):
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
        "Host": "locations.traderjoes.com",
        "Referer": referer,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }


def fetch_data():
    locator_domain = "https://www.traderjoes.com/"
    base_url = "https://locations.traderjoes.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers()).text, "lxml")
        states = soup.select("div.itemlist a")
        logger.info(f"{len(states)} found")
        for state in states:
            sp1 = bs(session.get(state["href"], headers=_headers()).text, "lxml")
            cities = sp1.select("div.itemlist a")
            logger.info(f"[{state.text}]{len(cities)} found")
            for city in cities:
                sp2 = bs(
                    session.get(city["href"], headers=_headers(state["href"])).text,
                    "lxml",
                )
                locations = sp2.select("div.itemlist a.directions")
                logger.info(f"[{state.text}][{city.text}] {len(locations)} found")
                for loc in locations:
                    sp2 = bs(
                        session.get(loc["href"], headers=_headers(city["href"])).text,
                        "lxml",
                    )
                    cc = sp2.select_one("p.opening-comments")
                    if cc and (
                        "coming soon" in cc.text.lower()
                        or "opening" in cc.text.lower()
                        or "opens" in cc.text.lower()
                    ):
                        continue
                    addr = list(sp2.select_one("div.addressline").stripped_strings)
                    hours = [_.text for _ in sp2.select("div#hoursSpl p")]
                    yield SgRecord(
                        page_url=loc["href"],
                        location_name=loc.text.replace(
                            "View Store Details for", ""
                        ).strip(),
                        street_address=addr[0],
                        city=addr[1].split(",")[0].strip(),
                        state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                        zip_postal=addr[1]
                        .split(",")[1]
                        .strip()
                        .split(" ")[-1]
                        .strip()
                        .replace("?", ""),
                        latitude=sp2.select_one(
                            'meta[property="place:location:latitude"]'
                        )["content"],
                        longitude=sp2.select_one(
                            'meta[property="place:location:longitude"]'
                        )["content"],
                        country_code="US",
                        phone=sp2.select_one("div.mobile").text.strip(),
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
