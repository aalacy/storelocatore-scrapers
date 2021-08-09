from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.kfc.hr"
base_url = "http://www.kfc.hr/restorani/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split('$("#map1").maps(')[1]
            .split(').data("wpgmp_maps")')[0]
        )["places"]
        for _ in locations:
            addr = _["location"]
            hours = []
            temp = list(bs(_["content"], "lxml").stripped_strings)
            for x, hh in enumerate(temp):
                if "Radno vrijeme:" in hh:
                    for hr in temp[x + 1 :]:
                        if "Drive Thru" in hr:
                            break
                        hours.append(hr)

            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=_["address"].split(",")[0].strip(),
                city=addr["city"],
                state=addr["state"],
                zip_postal=addr["postal_code"],
                latitude=addr["lat"],
                longitude=addr["lng"],
                country_code=addr["country"],
                locator_domain=locator_domain,
                hours_of_operation=" ".join(hours).replace("-", "-").replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
