import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://mcdonalds.gr/wp-admin/admin-ajax.php"
    domain = "mcdonalds.gr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get("https://mcdonalds.gr/locate/")
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "wpjs")]/text()')[0]
    data = re.findall("wpjs =(.+);", data)[0]
    data = json.loads(data)

    frm = {"action": "get_locations", "token": data["ajax_nonce"]}
    data = session.post(start_url, headers=hdr, data=frm).json()

    all_locations = data["data"]
    for poi in all_locations:
        page_url = poi["permalink"]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//table[@class="location-hours-table"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo).split(" Δευτέρα")[0]
        if poi["latlng"].get("street_name"):
            if poi["latlng"].get("street_number"):
                street_address = (
                    f'{poi["latlng"]["street_name"]} {poi["latlng"]["street_number"]}'
                )
            else:
                street_address = poi["latlng"]["street_name"]
        else:
            street_address = poi["latlng"]["address"].split(",")[0]
        if "McDonald" in street_address:
            street_address = etree.HTML(poi["address"]).xpath("//text()")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["permalink"],
            location_name=poi["title"].replace("&#8211;", "-"),
            street_address=street_address,
            city=poi["latlng"]["city"],
            state=poi["latlng"].get("state"),
            zip_postal=poi["latlng"]["post_code"],
            country_code=poi["latlng"]["country_short"],
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=poi["latlng"]["lat"],
            longitude=poi["latlng"]["lng"],
            hours_of_operation=hours_of_operation,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
