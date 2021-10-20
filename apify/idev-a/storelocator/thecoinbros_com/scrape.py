from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("thecoinbros")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.thecoinbros.com"
base_url = "https://www.thecoinbros.com/locations"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("pointONE =")[1]
            .split("point2 =")[0]
            .strip()[:-1]
        )
        for _ in locations:
            sp1 = bs(_[2], "lxml")
            addr = list(sp1.select_one(".location-address").stripped_strings)
            c_s = addr[1].split(" ")
            page_url = sp1.select_one("a.titlePin")["href"]
            logger.info(page_url)
            sp2 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            if sp2.select_one("div.miniSection.hours"):
                days = list(
                    sp2.select_one(
                        "div.miniSection.hours div.fusion-row div.fusion-column-first"
                    ).stripped_strings
                )
                times = list(
                    sp2.select_one(
                        "div.miniSection.hours div.fusion-row div.fusion-column-last"
                    ).stripped_strings
                )
                for hh in zip(days, times):
                    hours.append(": ".join(hh))
            zip_postal = c_s[-2].strip()
            city = state = ""
            if zip_postal.isdigit():
                city = " ".join(c_s[:-3])
                state = c_s[-3]
            else:
                zip_postal = ""
                city = " ".join(c_s[:-2])
                state = c_s[-2]
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h4.text.replace("&#8217;", "'").strip(),
                street_address=addr[0],
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=_[0],
                longitude=_[1],
                country_code=c_s[-1],
                phone=sp2.select_one("div.headline a strong").text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
