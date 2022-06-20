import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "twinpeaksrestaurant.com"
    start_url = "https://twinpeaksrestaurant.com/api/locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        location_type = "<MISSING>"
        if poi["acf"]["market"]:
            location_type = poi["acf"]["market"]["post_type"]
        if poi["acf"]["status"] == "coming_soon":
            continue
        hoo = []
        if poi["acf"]["hours"]:
            for elem in poi["acf"]["hours"]:
                day = elem["day"]["label"]
                opens = elem["opens"]
                closes = elem["closes"]
                hoo.append(f"{day} {opens} - {closes}")
        hoo = " ".join(hoo) if hoo else ""
        state = ""
        if type(poi["acf"]["state"]) == dict:
            state = poi["acf"]["state"]["value"]

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["link"],
            location_name=poi["acf"]["city"],
            street_address=poi["acf"]["address"],
            city=poi["acf"]["city"],
            state=state,
            zip_postal=poi["acf"]["postal"],
            country_code=poi["acf"]["country"]["value"],
            store_number=poi["id"],
            phone=poi["acf"]["phone_number"],
            location_type=location_type,
            latitude=poi["acf"]["latitude"],
            longitude=poi["acf"]["longitude"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
