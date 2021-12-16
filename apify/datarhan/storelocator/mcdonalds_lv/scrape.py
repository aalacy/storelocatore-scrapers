import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://mcdonalds.lv/wp-admin/admin-ajax.php"
    domain = "mcdonalds.lv"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get("https://mcdonalds.lv/atrodi/")
    token = re.findall('ajax_nonce":"(.+?)"', response.text)[0]
    frm = {"action": "get_locations", "token": token}
    data = session.post(start_url, headers=hdr, data=frm).json()

    for poi in data["data"]:
        page_url = poi["permalink"]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        street_address = ""
        if poi["latlng"].get("street_name"):
            street_address = (
                f'{poi["latlng"]["street_name"]} {poi["latlng"]["street_number"]}'
            )
        else:
            street_address = etree.HTML(poi["infoWindowContent"]).xpath(
                '//div[@class="address"]/p/text()'
            )[0]
        phone = etree.HTML(poi["infoWindowContent"]).xpath(
            '//a[contains(@href, "tel")]/text()'
        )
        phone = phone[0] if phone else ""
        hoo = loc_dom.xpath(
            '//div[a[contains(text(), "Restorāns")]]/following-sibling::div//table[@class="location-hours-table"]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["title"],
            street_address=street_address,
            city=poi["latlng"]["city"],
            state=poi["latlng"].get("state"),
            zip_postal=poi["latlng"]["post_code"],
            country_code=poi["latlng"]["country_short"],
            store_number=poi["ID"],
            phone=phone,
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
