from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from datetime import date, timedelta
import calendar
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mercadona.es/"
base_url = (
    "https://www.mercadona.com/estaticos/cargas/data.js?timestamp=%271637883948973%27"
)
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            locations = json.loads(
                session.get(base_url, headers=_headers)
                .text.split("var dataJson =")[1]
                .strip()[:-1]
            )["tiendasFull"]
            curr_date = date.today()
            next_date = curr_date + timedelta(days=1)
            today = calendar.day_name[curr_date.weekday()]
            tomorrow = calendar.day_name[next_date.weekday()]
            for _ in locations:
                page_url = f"https://info.mercadona.es/en/supermarkets?k={_['id']}"
                logger.info(page_url)
                driver.get(page_url)
                sp1 = bs(driver.page_source, "lxml")
                hours = []
                for day in days:
                    for hh in sp1.select("div.panelDetalleElemento ul")[0].select("li"):
                        hr = (
                            " ".join(hh.stripped_strings)
                            .replace("Today", today)
                            .replace("Tomorrow", tomorrow)
                        )
                        if day in hr:
                            hours.append(hr)

                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["lc"],
                    street_address=_["dr"],
                    city=_["pv"],
                    zip_postal=_["cp"],
                    country_code=_["p"],
                    latitude=_["lt"],
                    longitude=_["lg"],
                    phone=_.get("tf"),
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
