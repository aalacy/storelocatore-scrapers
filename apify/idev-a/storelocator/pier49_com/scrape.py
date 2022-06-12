from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from sgselenium import SgChrome
import dirtyjson as json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("pier49")

locator_domain = "https://pier49.com"
base_url = "https://pier49.com/locations/"


def _url(locs, city):
    for loc in locs:
        if city in loc.text:
            return loc["href"]


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        locs = soup.select_one(
            "div#content div.section-content div.align-middle.align-center"
        ).select("a")
        links = soup.select("section.section.has-parallax div.medium-6")
        logger.info(f"{len(links)} found")
        for link in links:
            if link.select_one("div.img"):
                continue
            addr = [aa.text.strip() for aa in link.select("p")]
            if "DELIVERY ONLY" in addr[0]:
                continue
            city = addr[2].split(",")[0].strip()

            try:
                _link = link.find(
                    "span", string=re.compile(r"Order Online")
                ).find_parent()
                page_url = _link["href"]
                if "/restaurants" not in page_url or "hidden" in _link["class"]:
                    page_url = ""
            except:
                page_url = ""
            if not page_url:
                page_url = _url(locs, city)
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
                    driver.get(page_url)
                    logger.info(page_url)
                    try:
                        sp1 = bs(driver.page_source, "lxml")
                        ss = json.loads(
                            sp1.find("script", type="application/ld+json").string
                        )
                        latitude = ss["geo"]["latitude"]
                        longitude = ss["geo"]["longitude"]
                    except:
                        loc_id = page_url.split("/")[-1]
                        json_url = f"restaurants/{loc_id}"
                        if loc_id.isdigit():
                            rr = driver.wait_for_request(json_url)
                            ss = json.loads(rr.response.body)["restaurant"]
                            latitude = ss["latitude"]
                            longitude = ss["longitude"]

            _hr = link.find("", string=re.compile(r"^Hours")).find_parent("h3")
            hours = []
            if _hr:
                for hh in _hr.find_next_siblings("p"):
                    _hh = hh.text.strip()
                    if (
                        "open" in _hh.lower()
                        or "delivery" in _hh.lower()
                        or "lunch" in _hh.lower()
                    ):
                        break
                    hours.append(_hh)

            yield SgRecord(
                page_url=page_url,
                location_name=link.h3.text.strip(),
                street_address=addr[1],
                city=city,
                state=addr[2].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[2].split(",")[1].strip().split()[-1].strip(),
                country_code="US",
                phone=addr[0],
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(addr[1:3]),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
