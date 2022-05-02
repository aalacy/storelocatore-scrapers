from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://burgerking.co.kr"
base_url = "https://burgerking.co.kr/store/selectStore.json?message=%7B%22header%22%3A%7B%22error_code%22%3A%22%22%2C%22error_text%22%3A%22%22%2C%22info_text%22%3A%22%22%2C%22login_session_id%22%3A%22%22%2C%22message_version%22%3A%22%22%2C%22result%22%3Atrue%2C%22trcode%22%3A%22store%2FselectStore%22%2C%22ip_address%22%3A%22%22%2C%22platform%22%3A%2202%22%2C%22id_member%22%3A%22%22%2C%22auth_token%22%3A%22%22%2C%22cd_membership%22%3A%22%22%7D%2C%22body%22%3A%7B%22addrSi%22%3A%22%22%2C%22addrGu%22%3A%22%22%2C%22dirveTh%22%3A%22%22%2C%22dlvyn%22%3A%22%22%2C%22kmonYn%22%3A%22%22%2C%22kordYn%22%3A%22%22%2C%22oper24Yn%22%3A%22%22%2C%22parkingYn%22%3A%22%22%2C%22distance%22%3A%223%22%2C%22sortType%22%3A%22DISTANCE%22%2C%22storCoordX%22%3A%22{}%22%2C%22storCoordY%22%3A%22{}%22%2C%22storNm%22%3A%22%22%7D%7D"
hr_obj = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}


def fetch_data(search):
    for lat, lng in search:
        with SgRequests() as session:
            locations = session.get(base_url.format(lng, lat), headers=_headers).json()[
                "body"
            ]["storeList"]
            if locations:
                search.found_location_at(lat, lng)
            logger.info(f"[{lat, lng}] {len(locations)}")
            for _ in locations:
                addr = _["ADDR_1"]
                if _["ADDR_2"]:
                    addr += " " + _["ADDR_2"]
                addr = addr.strip()
                hours = _["STORE_TIME"].split(",")
                if not hours:
                    if _["KING_ORDER_STATE_OF_WEEK_DAY"]:
                        hours = []
                        for hh in json.loads(_["KING_ORDER_STATE_OF_WEEK_DAY"]):
                            hours.append(
                                f"{hr_obj[hh['dayOfWeek']]}: {hh['kingOrderOpenTime']}-{hh['kingOrderCloseTime']}"
                            )

                yield SgRecord(
                    page_url="https://burgerking.co.kr/#/store",
                    store_number=_["STOR_CD"],
                    location_name=_["STOR_NM"],
                    street_address=" ".join(addr.split(" ")[1:]),
                    city=addr.split(" ")[0],
                    latitude=_["STOR_COORD_Y"],
                    longitude=_["STOR_COORD_X"],
                    country_code="South Korea",
                    phone=_["TEL_NO"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours)
                    .replace("Cleaning Day(Close):", "")
                    .strip(),
                    raw_address=addr,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.KOREA_S], granularity=Grain_8()
        )
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
