from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.structube.com"
base_url = "https://www.structube.com/graphql?query=query+storesByOrigin%28%24latitude%3AFloat%24longitude%3AFloat%24radius%3AInt%24useInLocator%3ABoolean%24useInPickup%3ABoolean%29%7BabsoStores%28origin%3A%7Blatitude%3A%24latitude+longitude%3A%24longitude+radius%3A%24radius%7Duse_in_locator%3A%24useInLocator+use_in_pickup%3A%24useInPickup%29%7Btotal_count+items%7Bentity_id+identifier+name+url_key+address1+address2+city+country_id+region+region_id+telephone+type+email+postcode+latitude+longitude+is_active+more_infos+special_schedule+opening_hours%7Bitems%7Bclose+open+day+__typename%7D__typename%7D__typename%7D__typename%7D%7D&operationName=storesByOrigin&variables=%7B%22latitude%22%3Anull%2C%22longitude%22%3Anull%2C%22radius%22%3A5%2C%22useInLocator%22%3Atrue%7D"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["data"][
            "absoStores"
        ]["items"]
        for _ in locations:
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]
            page_url = "https://www.structube.com/en_ca/" + _["url_key"]
            hours = []
            for hh in _.get("opening_hours", {}).get("items", []):
                hours.append(f"{hh['day']}: {hh['open']} - {hh['close']}")
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["region"],
                zip_postal=_["postcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country_id"],
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
