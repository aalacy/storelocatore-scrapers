from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import json
import re

logger = SgLogSetup().get_logger("frontgate")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.frontgate.com"
    base_url = "https://www.frontgate.com/store-locs/content"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#category div.col-xs-6.col-sm-4")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            block = list(_.address.stripped_strings)
            addr = parse_address_intl(" ".join(block[:-1]))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            page_url = locator_domain + _.a["href"]
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            logger.info(page_url)
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div.hoursOpenInfo_container .col-xs-2")[1:]
            ]
            if not hours:
                _hr = sp1.find("h3", string=re.compile(r"Hours"))
                if _hr:
                    for hh in _hr.find_next_siblings():
                        if "Store hours" in hh.text:
                            break
                        hours.append(": ".join(hh.stripped_strings))
            script = json.loads(
                sp1.find("script", type="application/ld+json").string.strip()
            )
            yield SgRecord(
                page_url=page_url,
                location_name=_.strong.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[-1].split(":")[-1].replace("Phone", ""),
                locator_domain=locator_domain,
                latitude=script["geo"]["latitude"],
                longitude=script["geo"]["longitude"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
