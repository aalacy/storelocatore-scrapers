from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium import SgChrome
from sgscrape.sgpostal import parse_address_intl
import re
import time
import json

logger = SgLogSetup().get_logger("arshealth")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://arshealth.com/"
    base_url = "https://arshealth.com/ars-mid-atlantic-locations/"
    json_url = "https://arshealth.com/wp-json/wpgmza/v1/features/"
    with SgRequests() as session:
        with SgChrome() as driver:
            driver.get(base_url)
            links = [
                ll
                for ll in bs(driver.page_source, "lxml").select(
                    ".vc_row.wpb_row.section.vc_row-fluid .wpb_column.vc_column_container"
                )[2:-1]
                if ll.h4
            ]
            exist = False
            while not exist:
                time.sleep(1)
                for rr in driver.requests:
                    if rr.url.startswith(json_url) and rr.response:
                        exist = True
                        locations = json.loads(rr.response.body)["markers"]
                        for x, _ in enumerate(locations):
                            page_url = links[x].a["href"]
                            logger.info(page_url)
                            sp1 = bs(
                                session.get(page_url, headers=_headers).text, "lxml"
                            )
                            hours = []
                            _hr = sp1.find("h5", string=re.compile(r"Office Hours"))
                            if _hr:
                                hours = [
                                    hh
                                    for hh in _hr.find_next_sibling(
                                        "p"
                                    ).stripped_strings
                                    if "Admissions" not in hh
                                ]
                            addr = parse_address_intl(_["address"])
                            street_address = addr.street_address_1
                            if addr.street_address_2:
                                street_address += " " + addr.street_address_2
                            phone = ""
                            if sp1.find("a", href=re.compile(r"tel:")):
                                phone = sp1.find(
                                    "a", href=re.compile(r"tel:")
                                ).text.strip()
                            yield SgRecord(
                                page_url=page_url,
                                store_number=_["id"],
                                location_name=" ".join(links[x].h4.stripped_strings),
                                street_address=street_address,
                                city=addr.city,
                                state=addr.state,
                                zip_postal=addr.postcode,
                                country_code="US",
                                phone=phone,
                                latitude=_["lat"],
                                longitude=_["lng"],
                                locator_domain=locator_domain,
                                hours_of_operation="; ".join(hours).replace("–", "-"),
                                raw_address=_["address"],
                            )

                        break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
