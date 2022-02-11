from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_8

logger = SgLogSetup().get_logger("takebackday")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://takebackday.dea.gov/"
base_url = "https://apps2.deadiversion.usdoj.gov/pubdispsearch/spring/main"


def fetch_data(search):
    with SgRequests() as session:
        for zip in search:
            rr = session.get(base_url, headers=_headers)
            execution = rr.url.query.decode().split("execution=")[-1]
            data = {
                "searchForm": "searchForm",
                "searchForm:zipCodeInput": zip,
                "searchForm:cityInput": "",
                "searchForm:stateInput_focus": "",
                "searchForm:stateInput_input": "",
                "searchForm:radiusInput": "50",
                "searchForm:submitSearchButton": "",
                "javax.faces.ViewState": execution,
            }
            res = session.post(
                base_url + f"?execution={execution}", headers=_headers, data=data
            )
            if res.status_code != 200:
                continue
            soup = bs(res.text, "lxml")
            if "An unexpected error" in soup.text:
                continue
            locations = soup.select("table tbody tr")
            logger.info(f"[{zip}] {len(locations)} found")
            for _ in locations:
                td = _.select("td")
                if len(td) == 1:
                    continue
                addr = [dd.text.strip() for dd in td[1:4]]
                street_address = addr[0]
                if addr[1]:
                    street_address += " " + addr[1]
                yield SgRecord(
                    location_name=list(td[0].stripped_strings)[-1],
                    street_address=street_address,
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[-1].strip().split()[0].strip(),
                    zip_postal=addr[-1].split(",")[-1].strip().split()[-1].strip(),
                    country_code="US",
                    locator_domain=locator_domain,
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS}),
            duplicate_streak_failure_factor=100,
        )
    ) as writer:
        search = DynamicZipSearch(
            country_codes=[SearchableCountries.USA], granularity=Grain_8()
        )
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
