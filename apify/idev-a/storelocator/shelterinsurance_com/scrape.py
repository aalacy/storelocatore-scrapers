from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson as json
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("shelterinsurance")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.shelterinsurance.com"
    base_url = "https://www.shelterinsurance.com/CA/agent/search"
    with SgRequests() as session:
        states = (
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .find("p", string=re.compile(r"By state:"))
            .find_next_sibling("ul")
            .select("a")
        )
        for state in states:
            state_url = locator_domain + state["href"]
            cities = bs(session.get(state_url, headers=_headers).text, "lxml").select(
                "div.columns.seven.offset-by-one ul a"
            )
            for city in cities:
                city_url = locator_domain + city["href"]
                page = 1
                while True:
                    soup = bs(
                        session.get(f"{city_url}?Page={page}", headers=_headers).text,
                        "lxml",
                    )
                    links = soup.select("div.agentResults div.result")
                    if not links:
                        break
                    logger.info(
                        f"[{state.text.strip()}][page {page}][count {len(links)}][{city.text.strip()}]"
                    )
                    page += 1
                    for link in links:
                        phone = ""
                        if link.find("a", href=re.compile(r"tel:")):
                            phone = link.find(
                                "a", href=re.compile(r"tel:")
                            ).text.strip()
                        page_url = (
                            locator_domain + link.select_one("div.agentName a")["href"]
                        )
                        logger.info(page_url)
                        addr = list(
                            link.select(
                                "div.agentResults div.result div.three.columns"
                            )[1].stripped_strings
                        )[-2:]
                        coord = json.loads(link["data-jmapping"])
                        yield SgRecord(
                            page_url=page_url,
                            store_number=link["data-agent-index"],
                            location_name=link.select_one("div.agentName a")
                            .text.split(".")[-1]
                            .strip(),
                            street_address=addr[0],
                            city=addr[1].split(",")[0].strip(),
                            state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                            zip_postal=addr[1]
                            .split(",")[1]
                            .strip()
                            .split(" ")[-1]
                            .strip(),
                            country_code="US",
                            phone=phone,
                            locator_domain=locator_domain,
                            latitude=coord["point"]["lat"],
                            longitude=coord["point"]["lng"],
                        )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
