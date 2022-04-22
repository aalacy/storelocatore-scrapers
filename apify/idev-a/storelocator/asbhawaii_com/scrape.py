from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("asbhawaii")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.asbhawaii.com"
base_url = "https://www.asbhawaii.com/locations"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location-item")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link.a["href"]
            if "locations" not in page_url:
                page_url = ""
            addr = [
                aa.text.replace("\t", "").replace("\n", " ").strip()
                for aa in link.select("ul")[0].select("li")[1:-1]
            ]
            hours = [
                "".join(hh.stripped_strings)
                for hh in link.select("div.open-time div.row ul")
            ]
            if "closed" in link.select(".sh-c")[2].text.strip():
                hours = ["temporarily closed"]
            coord = (
                link.find("a", string=re.compile(r"Get Directions"))["href"]
                .split("&ll=")[1]
                .split("&")[0]
                .split(",")
            )
            location_type = "branch"
            location_name = link.strong.text.strip()
            if "atm" in location_name.lower():
                location_type = "atm"
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split()[0].strip(),
                zip_postal=link["data-zip"],
                country_code="US",
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                location_type=location_type,
                hours_of_operation="; ".join(hours)
                .replace("–", "-")
                .replace("\n", "; ")
                .replace("\r", "")
                .replace("\t", ""),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
