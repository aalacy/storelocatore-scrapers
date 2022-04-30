from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import dirtyjson as json
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("amerisleep")

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}
locator_domain = "https://amerisleep.com"
base_url = "https://amerisleep.com/retail/"


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("-", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa", "")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "html.parser")
        divlist = soup.select("div.retail-locations-column-info")
        for div in divlist:
            link = div.a["href"]
            if not link.startswith("http"):
                link = locator_domain + link
            logger.info(link)
            soup1 = bs(session.get(link, headers=_headers).text, "lxml")
            loc = json.loads(
                soup1.find("script", type="application/ld+json")
                .string.strip()
                .replace("\n", "")
            )
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in soup1.select("div.store-hours div.store-hours__row")
            ]
            coord = (
                soup1.select_one("div.retail-phone a.button")["href"]
                .split("!3d")[1]
                .split("?")[0]
                .split("!4d")
            )
            yield SgRecord(
                page_url=link,
                location_name=loc["name"],
                street_address=loc["address"]["streetAddress"],
                city=loc["address"]["addressLocality"],
                state=loc["address"]["addressRegion"],
                zip_postal=loc["address"]["postalCode"],
                country_code="US",
                location_type=loc["@type"],
                phone=loc["telephone"],
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
