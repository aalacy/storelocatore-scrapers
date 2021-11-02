from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import us

logger = SgLogSetup().get_logger("takebackday")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://takebackday.dea.gov/"
base_url = "https://apps2.deadiversion.usdoj.gov/NTBI/ntbi.do?_flowId=public-lite-flow"


def fetch_data():
    with SgRequests() as session:
        for state in us.states.STATES:
            data = {
                "zipCode_P": "",
                "county_P": "",
                "city_P": "",
                "state_P": state.abbr,
                "searchRadius": "5000",
                "_eventId_submit": "Submit",
            }
            res = session.post(base_url, headers=_headers, data=data)
            if res.status_code != 200:
                logger.warning(state.abbr)
                continue
            soup = bs(res.text, "lxml")
            if "An unexpected error" in soup.text:
                logger.warning(state.abbr)
                continue
            temp = " ".join(
                list(soup.select_one("div#tableie h2").stripped_strings)
            ).split("\n")[1:]
            hours = []
            hours.append(temp[0].split(",")[0])
            hours.append(temp[1])
            locations = soup.select("table tbody tr")
            logger.info(f"[{state.abbr}] {len(locations)} found")
            for _ in locations:
                td = _.select("td")
                if len(td) == 1:
                    continue
                raw_address = (
                    td[1]
                    .a["href"]
                    .split("&daddr=")[1]
                    .split("&hl")[0]
                    .replace("+", " ")
                )
                addr = raw_address.split(",")
                yield SgRecord(
                    location_name=f"DRUG DISPOSAL SITE AT {list(td[0].stripped_strings)[0]}",
                    street_address=" ".join(addr[:-2]),
                    city=addr[-2],
                    state=addr[-1].strip().split(" ")[0].strip(),
                    zip_postal=addr[-1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    locator_domain=locator_domain,
                    hours_of_operation=": ".join(hours)
                    .replace("Take Back Day:", "")
                    .replace("\t", ""),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
