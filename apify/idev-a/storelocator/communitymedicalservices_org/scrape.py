from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("communitymedicalservices")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://communitymedicalservices.org/"
    base_url = "https://communitymedicalservices.org/locations/"
    with SgRequests() as session:
        links = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var mapsvg_options =")[1]
            .split(";jQuery.extend")[0]
            .strip()
        )["data_db"]["objects"]
        logger.info(f"{len(links)} found")
        for _ in links:
            page_url = _["link"].strip()
            if not _["title"] or not page_url or page_url == "#":
                continue
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _pp = sp1.find("h4", string=re.compile(r"Phone:"))
            phone = ""
            if _pp:
                phone = (
                    list(_pp.find_next_sibling().stripped_strings)[0]
                    .split(":")[-1]
                    .replace("Phone", "")
                )
            addr = list(
                sp1.find("h4", string=re.compile(r"Location:"))
                .find_next_sibling("p")
                .stripped_strings
            )
            _hr = sp1.find(
                "script",
                src=re.compile(r"https://knowledgetags.yextpages.net/embed"),
            )
            hours = []
            if _hr:
                res = session.get(_hr["src"], headers=_headers).text
                if "Entity not found" not in res:
                    hours = json.loads(res.split("Yext._embed(")[1][:-1].strip())[
                        "entities"
                    ][0]["attributes"]["hours"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code=_["location"]["address"].get("country_short"),
                phone=phone,
                locator_domain=locator_domain,
                latitude=_["location"]["lat"],
                longitude=_["location"]["lng"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=_["location"]["address"]["formatted"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
