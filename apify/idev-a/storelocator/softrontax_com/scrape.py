from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
import dirtyjson as json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("softrontax")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locator_domain = "https://www.softrontax.com"
    base_url = "https://www.softrontax.com/location"
    with SgRequests(verify_ssl=False) as http:
        locations = bs(http.get(base_url, headers=_headers), "lxml").select(
            "div.container div.column li a"
        )
        for loc in locations:
            url = locator_domain + loc["href"]
            locs = json.loads(
                bs(http.get(url, headers=_headers).text, "lxml")
                .select_one("script#__NEXT_DATA__")
                .string
            )["props"]["pageProps"]["location_data"]
            for _ in locs:
                hours = []
                for x, hh in enumerate(_["times"]):
                    hours.append(f"{days[x]}: {hh}")
                yield SgRecord(
                    page_url=f"https://www.softrontax.com/location/{_['id']}",
                    location_name=_["locationtitle"],
                    street_address=_["address"],
                    city=_["city"].split(",")[0].strip(),
                    state=_["city"].split(",")[-1].strip(),
                    zip_postal=_["pcode"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="CA",
                    phone=_["pnumber"].split("/")[0],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )
            break


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
