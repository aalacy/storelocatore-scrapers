from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.runnings.com/"
base_url = "https://www.runnings.com/graphql?query=query+GetAllStores%7Bstores%28filter%3A%7B%7DpageSize%3A60%29%7Bitems%7Bid+name+status+source_code+email+latitude+longitude+google_map_link+link+description+image+storelocator_open_time+storelocator_closed_time+store_identifier+warehouse_identifier+opening_hours+special_hours+recurring_hours+address+city+country_id+region+region_code+postcode+phone+meta_title+meta_description+meta_keywords+features+manager_name+manager_post+manager_photo+icon+fax+__typename%7D__typename%7D%7D&operationName=GetAllStores&variables=%7B%7D"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["data"]["stores"][
            "items"
        ]
        for _ in locations:
            page_url = (
                f"https://www.runnings.com/storelocator/store/{_['store_identifier']}"
            )
            hours = []
            for hh in json.loads(_["recurring_hours"]):
                hours.append(f"{hh['name']}: {hh['start_time']} - {hh['end_time']}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"].strip(),
                street_address=_["address"],
                city=_["city"],
                state=_["region_code"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                zip_postal=_["postcode"],
                country_code=_["country_id"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
