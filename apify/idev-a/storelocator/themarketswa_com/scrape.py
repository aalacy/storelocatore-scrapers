from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
import json

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


locator_domain = "https://www.themarketswa.com"
base_url = "https://www.themarketswa.com/"


def fetch_data():
    with SgRequests() as http:
        soup = bs(http.get(base_url, headers=_headers), "lxml")
        locations = (
            soup.find("a", string=re.compile(r"^Stores"))
            .find_next_sibling()
            .select("li a")
        )
        for _ in locations:
            page_url = locator_domain + _["href"]
            sp1 = bs(http.get(page_url, headers=_headers), "lxml")
            ss = json.loads(sp1.select_one("div.sqs-block-map")["data-block-json"])[
                "location"
            ]
            zip_postal = ss["addressLine2"].split(",")[1].strip().split(" ")[-1].strip()
            if not zip_postal.isdigit():
                zip_postal = ""

            addr = sp1.find("h2", string=re.compile(r"^Location:"))
            street_address = ss["addressLine1"]
            if addr:
                street_address = list(addr.find_next_sibling("p").stripped_strings)[0]
            yield SgRecord(
                page_url=page_url,
                location_name=ss["addressTitle"],
                street_address=street_address,
                city=ss["addressLine2"].split(",")[0].strip(),
                state=ss["addressLine2"].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=zip_postal,
                country_code="US",
                locator_domain=locator_domain,
                raw_address=ss["addressLine1"] + ", " + ss["addressLine2"],
                phone=sp1.select(
                    "section#page div.sqs-block-html div.sqs-block-content h3"
                )[-2].text.strip(),
                latitude=ss["mapLat"],
                longitude=ss["mapLng"],
                hours_of_operation=sp1.select(
                    "section#page div.sqs-block-html div.sqs-block-content h3"
                )[-1].text.strip(),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
