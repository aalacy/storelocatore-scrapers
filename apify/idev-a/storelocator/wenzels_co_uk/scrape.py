from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.wenzels.co.uk"
base_url = "https://www.wenzels.co.uk/find-us/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var bhStoreLocatorLocations =")[1]
            .split("/* ]]> */")[0]
            .strip()[1:-2]
            .replace('\\"', '"')
            .replace("\\\\\\/", "/")
        )
        for _ in locations:
            street_address = _["address_1"]
            city = _["address_city"]
            if (
                not city
                and "Road" not in _["address_2"]
                and not street_address.startswith("Unit")
            ):
                city = _["address_2"]
            else:
                street_address += " " + _["address_2"]
            hours = []
            for x in range(1, 7):
                if _.get(f"hours{x}"):
                    hours.append(_[f"hours{x}"])
                else:
                    break
            state = ""
            if "Road" not in _["address_3"]:
                state = _["address_3"].replace("Shepherds Hill", "")
            if not city and state:
                city = state
                state = ""
            if _["name"] == "Crouch End":
                import pdb

                pdb.set_trace()
            yield SgRecord(
                page_url=_["permalink"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=city.replace("\\u00a0", " "),
                state=state,
                zip_postal=_["postcode"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="UK",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("\u2013", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
