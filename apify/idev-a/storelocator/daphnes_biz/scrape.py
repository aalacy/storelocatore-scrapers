from typing import List, Generator, Any
from functools import partial
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.simple_utils import parallelize
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json

locator_domain = "https://daphnes.biz/"
base_url = "https://easylocator.net/ajax/search_by_lat_lon_geojson/daphnes/%s/%s/500/150/null/null"


def _valid(val):
    return (
        val.replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
    )


def fetch_records_for(http: SgRequests, coord) -> Generator:
    res = http.get(base_url % (coord[0], coord[1]))
    yield json.loads(res.text)


def process_record(res: Generator) -> List[SgRecord]:
    _res = list(res)[0]
    if _res["physical"]:
        for _ in _res["physical"]:
            _ = _["properties"]
            hours = []
            for _hour in (
                bs(_["additional_info"], "lxml").select_one("div").stripped_strings
            ):
                if "Temporary Closed" in _hour:
                    hours.append("Closed")
                    break
                if "Hours" in _hour:
                    continue
                if "Online" in _hour:
                    break

                hours.append(_hour)

            hours_of_operation = _valid("; ".join(hours))
            record = SgRecord(
                store_number=_["location_number"],
                location_name=_["name"],
                street_address=_["street_address"],
                city=_["city"],
                state=_["state_province"],
                zip_postal=_["zip_postal_code"],
                country_code=_["country"],
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lon"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )
            return [record]

    return []


def uniq_record_id(record: SgRecord) -> Any:
    return record.as_dict()[SgRecord.Headers.STORE_NUMBER]


if __name__ == "__main__":
    with SgRequests() as http:
        with SgWriter() as writer:
            results = parallelize(
                search_space=static_coordinate_list(
                    radius=10, country_code=SearchableCountries.USA
                ),
                fetch_results_for_rec=partial(fetch_records_for, http),
                processing_function=process_record,
                max_threads=4,  # tweak to see what's fastest
            )
            for rec in results:
                writer.write_row(rec)
