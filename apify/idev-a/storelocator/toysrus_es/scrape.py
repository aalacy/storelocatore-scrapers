from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests.sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.toysrus.es"
base_url = "https://www.toysrus.es/store-finder?q=&page={}&latitude=40.416706&longitude=-3.7035825"


def fetch_records(http):
    page = 0
    locations = []
    while True:
        try:
            locations += http.get(base_url.format(page), headers=_headers).json()[
                "data"
            ]
        except:
            break
        page += 1

    logger.info(f"{len(locations)}")
    for _ in locations:
        addr = _["line1"].split(",")
        if _["town"] == addr[-1].strip():
            del addr[-1]
        hours = []
        for day, hh in _.get("openings", {}).items():
            hours.append(f"{day}: {hh}")
        yield SgRecord(
            page_url=locator_domain + _["url"],
            location_name=_["displayName"],
            street_address=", ".join(addr),
            city=_["town"],
            zip_postal=_["postalCode"],
            country_code="Spain",
            phone=_["phone"],
            latitude=_["latitude"],
            longitude=_["longitude"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
        )


if __name__ == "__main__":
    with SgRequests() as http:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            for rec in fetch_records(http):
                writer.write_row(rec)
