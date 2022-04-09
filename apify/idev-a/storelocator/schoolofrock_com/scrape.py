from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("schoolofrock")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.schoolofrock.com"
base_url = "https://www.schoolofrock.com/ajax/get-book-class-form-locations"


def fetch_records(http):
    locs = http.get(base_url, headers=_headers).json()["data"]["locations"]
    for _ in locs:
        page_url = _.get("url")
        if not page_url:
            continue
        logger.info(page_url)
        sp1 = bs(http.get(page_url, headers=_headers).text, "lxml")
        if sp1.select_one("div.wrapper"):
            txt = sp1.select_one("div.wrapper").text.lower()
            if "coming soon" in txt or "em breve mais uma" in txt:
                continue
        bar = sp1.select_one("div.promo-bar")
        if (
            bar
            and "coming soon" in bar.text.lower()
            and "black friday" in bar.text.lower()
            and "summer camp" in bar.text.lower()
        ):
            continue
        hours = [
            hh.text.replace("\n", "").replace("   ", "").strip()
            for hh in sp1.select("ul.open-hours li")
        ]

        street_address = _["address"]
        if _["suburb"]:
            street_address += " " + _["suburb"]
        phone = _.get("phone")
        if phone:
            phone = phone.split("/")[0].strip()
        yield SgRecord(
            page_url=page_url,
            store_number=_["id"],
            location_name=_["name"],
            street_address=street_address,
            city=_["city"],
            state=_.get("state"),
            zip_postal=_.get("zip"),
            country_code=_["country"],
            latitude=_["display_latitude"],
            longitude=_["display_longitude"],
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http):
                writer.write_row(rec)
