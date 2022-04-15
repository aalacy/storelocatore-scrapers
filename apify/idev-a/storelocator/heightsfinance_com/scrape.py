from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("hf")

locator_domain = "https://www.heightsfinance.com/"
base_url = "https://www.heightsfinance.com/wp-json/wp/v2/loan_office_location?_fields=acf,link,title&per_page=100&page={}"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    with SgRequests() as http:
        page = 1
        while True:
            try:
                res = http.get(base_url.format(page), headers=_headers)
                if res.status_code != 200:
                    break
                store_list = res.json()
                logger.info(f"[page {page}] {len(store_list)} found")
                page += 1
                for store in store_list:
                    page_url = store["link"]
                    logger.info(page_url)
                    street_address = store["acf"]["branch_address_1"]
                    if store["acf"]["branch_address_2"]:
                        street_address += " " + store["acf"]["branch_address_2"]
                    hours = []
                    _hr = bs(http.get(page_url, headers=_headers).text, "lxml").find(
                        "strong", string=re.compile(r"Office Hours:")
                    )
                    if _hr:
                        hours = list(
                            _hr.find_parent().find_next_sibling().stripped_strings
                        )
                        yield SgRecord(
                            page_url=page_url,
                            store_number=store["acf"]["branch_id"],
                            location_name=store["title"]["rendered"],
                            street_address=street_address,
                            city=store["acf"]["branch_city"],
                            state=store["acf"]["branch_state"],
                            zip_postal=store["acf"]["branch_zip"],
                            country_code="US",
                            locator_domain=locator_domain,
                            latitude=store["acf"].get("branch_latitude"),
                            longitude=store["acf"].get("branch_longitude"),
                            phone=store["acf"]["branch_phone_number"],
                            hours_of_operation="; ".join(hours),
                        )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
