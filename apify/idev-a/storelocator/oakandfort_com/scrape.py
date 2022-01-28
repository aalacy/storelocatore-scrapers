from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("oakandfort")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.oakandfort.com/"
    base_url = "https://www.oakandfort.com/sca-dev-2019-2/services/StoreLocator.Service.ss?c=4547545&locationtype=1&n=4&page={}&results_per_page=28&sort=namenohierarchy"
    with SgRequests() as session:
        locations = []
        page = 1
        while True:
            logger.info(f"page {page}")
            temp = session.get(base_url.format(page), headers=_headers).json()
            locations += temp["records"]
            page += 1
            if not temp["records"]:
                break
        for _ in locations:
            hours = []
            for hh in _["servicehours"]:
                days = []
                if hh["monday"] == "T":
                    days += ["Mon"]
                if hh["tuesday"] == "T":
                    days += ["Tue"]
                if hh["wednesday"] == "T":
                    days += ["Wed"]
                if hh["thursday"] == "T":
                    days += ["Thu"]
                if hh["friday"] == "T":
                    days += ["Fri"]
                if hh["saturday"] == "T":
                    days += ["Sat"]
                if hh["sunday"] == "T":
                    days += ["Sun"]
                if len(days) > 1:
                    days = f"{days[0]}-{days[-1]}"
                if len(days) == 1:
                    days = days[0]
                time = f"{hh['starttime']}-{hh['endtime']}"
                hours.append(f"{days}: {time}")

            page_url = f"https://www.oakandfort.com/stores/details/{_['internalid']}"
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]

            if not street_address and not _["city"] and not _["state"]:
                continue
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["internalid"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code=_["country"],
                latitude=_["location"]["latitude"],
                longitude=_["location"]["longitude"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
