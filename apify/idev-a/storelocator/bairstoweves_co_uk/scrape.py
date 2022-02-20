from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("bairstoweves")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.bairstoweves.co.uk"
base_url = "https://www.bairstoweves.co.uk/branches"
days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var branchData =")[1]
            .split("Homeflow.set")[0]
            .strip()[:-1]
        )["branches"]
        logger.info(f"{len(locations)}")
        for _ in locations:
            page_url = locator_domain + _["branchURL"]
            logger.info(page_url)
            ss = json.loads(
                session.get(page_url, headers=_headers)
                .text.split("Homeflow.set('branch_data',")[1]
                .split("Homeflow.set")[0]
                .strip()[:-2]
            )
            hours = []
            if ss["departments"]:
                for hh in ss["departments"][0]["openingTimes"]:
                    times = "closed"
                    if hh["open_time"] != "Closed":
                        times = f"{hh['open_time']} - {hh['close_time']}"
                    hours.append(f"{days[hh['day_of_week']]}: {times}")
            raw_address = _["address"].replace("\n", ", ")
            addr = raw_address.split(",")
            yield SgRecord(
                page_url=page_url,
                store_number=_["branchID"],
                location_name=_["name"],
                street_address=", ".join(addr[:-3]),
                city=addr[-3],
                state=addr[-2],
                zip_postal=addr[-1],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="UK",
                phone=_["contactNumber"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
