from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.chickendelight.com"
base_url = "https://www.chickendelight.com/wp-admin/admin-ajax.php?action=getlocations&lat=0&lng=0"


def fetch_data():
    with SgRequests() as session:
        locations = bs(
            session.get(base_url, headers=_headers).json()["html"], "lxml"
        ).select("li")
        province = ""
        for _ in locations:
            if _.get("class") == ["province"]:
                province = _.text.replace("–", "-").strip()
                continue
            phone = _.select("span")[-1].text.strip()
            street_address = _.select_one("a.name span").text.split("(")[0].strip()
            city = province.split("-")[-1].strip()
            street_address = street_address.split(city)[0].strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            page_url = _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            if sp1.select_one("p.hours"):
                hr = list(sp1.select_one("p.hours").stripped_strings)
                for hh in hr[1:]:
                    if "Holiday" in hh or "Delivery" in hh:
                        break

                    if "Hour" in hh:
                        break
                    hours.append(hh)
            raw_address = (
                sp1.select_one("h5.address")
                .text.replace("\n", " ")
                .replace("\r", " ")
                .strip()
            )
            addr = raw_address.split(",")
            if not street_address:
                street_address = addr[0]
            yield SgRecord(
                page_url=page_url,
                location_name=street_address,
                street_address=street_address,
                city=city,
                state=province.split("-")[0].strip(),
                latitude=sp1.select_one("div#gmap-wrap")["data-lat"],
                longitude=sp1.select_one("div#gmap-wrap")["data-lng"],
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
