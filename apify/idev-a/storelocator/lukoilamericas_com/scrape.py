from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("lukoilamericas")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://lukoilamericas.com"
base_url = "https://lukoilamericas.com/api/cartography/GetCountryDependentSearchObjectData?form=gasStation"
json_url = "https://lukoilamericas.com/api/cartography/GetObjects?lng=EN&{}"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        ids = session.get(base_url, headers=_headers).json()["GasStations"]
        for id in ids:
            res = session.get(
                json_url.format(f"ids=gasStation{id['GasStationId']}"), headers=_headers
            )
            logger.info(id["GasStationId"])
            if res.status_code != 200:
                continue
            loc = res.json()[0]
            _ = loc["GasStation"]
            hours = []
            if _["TwentyFourHour"]:
                hours = ["open 24h"]
            elif _["BusinessHoursForClient"]["BusinessHours"]:
                for hh in _["BusinessHoursForClient"]["BusinessHours"]:
                    hours.append(f"{hh['Days']}: {hh['Hours']}")
            elif _["StationBusinessHours"]:
                is_24h = True
                for x, hh in enumerate(_["StationBusinessHours"]["Days"]):
                    if hh["StartTime"] != "00:00:00" or hh["EndTime"] != "1.00:00:00":
                        is_24h = False
                    hours.append(
                        f"{days[x]}: {hh['StartTime'][:-3]} - {hh['EndTime'][:-3]}"
                    )
                if is_24h:
                    hours = ["open 24h"]

            page_url = f"https://lukoilamericas.com/en/ForMotorists/PetrolStations/PetrolStation?type=gasStation&id={_['GasStationId']}"
            if not _["Address"]:
                continue
            addr = parse_address_intl(_["Address"])
            yield SgRecord(
                page_url=page_url,
                store_number=_["GasStationId"],
                location_name=_["DisplayName"],
                street_address=_["Street"],
                city=_["City"],
                state=addr.state,
                zip_postal=_["PostCode"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code=addr.country,
                phone=_["Phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["Address"].replace("\n", " "),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
