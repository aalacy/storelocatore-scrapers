from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("shopsmartfoods")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://shopsmartfoods.com"
    base_url = (
        "https://shopsmartfoods.com/StoreLocator/Search/?ZipCode=95453&miles=1000"
    )
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#StoreLocator tr a")
        for link in links:
            addr = list(link.stripped_strings)
            state_zip = " ".join(addr[3:]).strip().split(" ")
            page_url = link["href"].replace("&amp;", "&")
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            phone = hours = ""
            if res.status_code == 200:
                sp1 = bs(res.text, "lxml")
                if sp1.find("a", href=re.compile(r"tel:")):
                    phone = sp1.find("a", href=re.compile(r"tel:")).text
                hours = sp1.select_one("table#hours_info-BS tr td dl dd").text
            yield SgRecord(
                page_url=page_url,
                location_name=addr[0],
                street_address=addr[1],
                city=addr[2],
                state=state_zip[1].strip(),
                zip_postal=state_zip[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
