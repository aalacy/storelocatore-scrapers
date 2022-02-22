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

locator_domain = "https://kfcrestaurants.be"
base_url = "https://kfcrestaurants.be/restaurants/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div#et-main-area div.et_pb_section div.et_pb_css_mix_blend_mode_passthrough"
        )
        for _ in locations:
            if not _.select_one(".et_pb_image") or not _.text.strip():
                continue
            if (
                _.select_one("p.p1")
                and _.select_one("p.p1").text.strip() == "Opent binnenkort"
            ):
                continue
            page_url = _.a["href"]
            logger.info(page_url)

            res = session.get(page_url, headers=_headers)
            if res.status_code != 200:
                continue
            sp1 = bs(res.text, "lxml")
            raw_address = (
                sp1.select_one("div.et_section_regular div.et_pb_text_inner p")
                .text.replace(",", "")
                .strip()
            )
            if "Bekijk Google Maps" == raw_address:
                raw_address = sp1.select_one(
                    "div.et_section_regular div.et_pb_text_inner h2"
                ).text
            street_address = sp1.select_one(
                "div.et_section_regular div.et_pb_text_inner h1"
            ).text
            _addr = raw_address.split()
            zip_postal = city = ""
            if len(_addr) > 2:
                street_address = _addr[0]
            if len(_addr) > 1:
                city = _addr[-1]
                zip_postal = _addr[-2]
            if raw_address.isdigit():
                zip_postal = raw_address
            try:
                coord = (
                    sp1.select_one("div.et_section_regular div.et_pb_text_inner p a")[
                        "href"
                    ]
                    .split("/@")[1]
                    .split("/data")[0]
                    .split(",")
                )
            except:
                try:
                    coord = (
                        sp1.select_one(
                            "div.et_section_regular div.et_pb_text_inner p a"
                        )["href"]
                        .split("[[")[1]
                        .split("],")[0]
                        .split(",")
                    )
                except:
                    coord = ["", ""]
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div.et_section_regular table tr")
            ]
            if not hours and sp1.select_one("div.et_section_regular .et_pb_text_1 p"):
                hours = list(
                    sp1.select_one(
                        "div.et_section_regular .et_pb_text_1 p"
                    ).stripped_strings
                )
            if not city:
                city = _.h4.text.split("|")[-1].strip()
            yield SgRecord(
                page_url=page_url,
                location_name=_.h4.text.strip(),
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                country_code="Belgium",
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours)
                .replace("–", "-")
                .replace("\xa0", "")
                .replace("     ", ":"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
