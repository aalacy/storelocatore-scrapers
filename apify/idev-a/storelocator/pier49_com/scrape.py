from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from sgselenium import SgFirefox
import json

logger = SgLogSetup().get_logger("pier49")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://pier49.com"
base_url = "https://pier49.com/locations/"


def fetch_data():
    with SgFirefox(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("section.section.has-parallax div.medium-6")
        logger.info(f"{len(links)} found")
        for link in links:
            if link.select_one("div.img"):
                continue
            try:
                page_url = link.find(
                    "span", string=re.compile(r"Order Online")
                ).find_parent()["href"]
                if "/restaurants" not in page_url:
                    page_url = ""
            except:
                page_url = ""
            latitude = longitude = ""
            try:
                latitude, longitude, temp = (
                    link.find("span", string=re.compile(r"Google Maps"))
                    .find_parent("a")["href"]
                    .split("/@")[1]
                    .split("/data")[0]
                    .split(",")
                )
            except:
                if page_url:
                    try:
                        driver.get(page_url)
                        logger.info(page_url)
                        sp1 = bs(driver.page_source, "lxml")
                        ss = json.loads(
                            sp1.find("script", type="application/ld+json").string
                        )
                        latitude = ss["geo"]["latitude"]
                        longitude = ss["geo"]["longitude"]
                    except:
                        import pdb

                        pdb.set_trace()
            addr = [aa.text.strip() for aa in link.select("p")]
            if "DELIVERY ONLY" in addr[0]:
                continue
            _hr = link.find("span", string=re.compile(r"Hours")).find_parent("h3")
            hours = []
            if _hr:
                for hh in _hr.find_next_siblings("p"):
                    if "open" in hh.text.lower() or "delivery" in hh.text.lower():
                        break
                    hours.append(hh.text.strip())

            yield SgRecord(
                page_url=page_url,
                location_name=link.h3.text.strip(),
                street_address=addr[1],
                city=addr[2].split(",")[0].strip(),
                state=addr[2].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[2].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[0],
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.PAGE_URL})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
