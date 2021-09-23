from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("germandonerkebab")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.germandonerkebab.com"
    base_url = "https://www.germandonerkebab.com/german-doner-kebab-store-locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.tabs-content div.tabs-panel")
        logger.info(f"{len(links)} found")
        for link in links:
            locations = link.select(".location-entry")
            logger.info(f"[{link['id']}] {len(locations)} found")
            for _ in locations:
                if _.select_one("img.location-banner"):
                    continue
                block = list(_.select_one(".location-details p").stripped_strings)
                _addr = (
                    block[0]
                    .replace("German Doner Kabab", "")
                    .replace("German Doner Kebab", "")
                    .strip()
                )
                if _addr.startswith(","):
                    _addr = _addr[1:].strip()
                addr = parse_address_intl(_addr)
                phone = ""
                if len(block) > 1:
                    phone = block[1].replace("Tel", "").strip()
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                if (
                    not street_address
                    or street_address.replace("-", "")
                    .replace(",", "")
                    .strip()
                    .isdigit()
                    or street_address.lower() == "dafza"
                ):
                    street_address = _addr.split(",")[0]
                zip_postal = addr.postcode
                _hr = _.find("strong", string=re.compile(r"NOW OPEN", re.IGNORECASE))
                if not _hr:
                    _hr = _.find(
                        "strong", string=re.compile(r"Open for", re.IGNORECASE)
                    )
                hours = []
                if _hr:
                    _hour = list(_hr.find_parent().stripped_strings)
                    if len(_hour) > 1:
                        for hh in _hour:
                            if "Open for" in hh:
                                continue
                            hours.append(hh)
                    else:
                        for hh in _hr.find_parent().find_next_siblings():
                            if not hh.text.strip():
                                break
                            if "Click here" in hh.text:
                                break
                            if "View map" in hh.text:
                                break
                            hours.append("; ".join(hh.stripped_strings))
                coord = ["", ""]
                page_url = base_url
                if _.select_one("a.click-for-more"):
                    page_url = _.select_one("a.click-for-more")["href"]
                    if not page_url.startswith("https"):
                        page_url = locator_domain + page_url
                    logger.info(page_url)
                    sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                    coord = (
                        sp1.select_one("div.map-responsive iframe")["src"]
                        .split("!2d")[1]
                        .split("!2m")[0]
                        .split("!3d")
                    )
                yield SgRecord(
                    page_url=page_url,
                    location_name=list(_.h2.stripped_strings)[0].replace("–", "-"),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=zip_postal,
                    country_code=link["id"],
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=coord[1],
                    longitude=coord[0],
                    hours_of_operation="; ".join(hours)
                    .replace("–", "-")
                    .replace("\xa0", ""),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
