import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.mcdonalds.com.mt/wp-admin/admin-ajax.php"
    domain = "mcdonalds.com.mt"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get("https://www.mcdonalds.com.mt/locate/")
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "wpjs")]/text()')[0]
    data = re.findall("wpjs =(.+);", data)[0]
    data = json.loads(data)

    frm = {"action": "get_locations", "token": data["ajax_nonce"]}
    data = session.post(start_url, headers=hdr, data=frm).json()

    for poi in data["data"]:
        page_url = poi["permalink"]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        street_address = ""
        if poi["latlng"].get("street_name"):
            street_address = (
                f'{poi["latlng"]["street_name"]} {poi["latlng"].get("street_number")}'
            ).strip()
        else:
            street_address = etree.HTML(poi["infoWindowContent"]).xpath(
                '//div[@class="address"]/p/text()'
            )[0]
        phone = etree.HTML(poi["infoWindowContent"]).xpath(
            '//a[contains(@href, "tel")]/text()'
        )
        phone = phone[0] if phone else ""
        hoo = loc_dom.xpath(
            '//div[a[contains(text(), "Restaurant")]]/following-sibling::div//table[@class="location-hours-table"]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["title"].replace("&#8220;", '"'),
            street_address=street_address,
            city=poi["latlng"]["city"],
            state=poi["latlng"].get("state"),
            zip_postal=poi["latlng"].get("post_code"),
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
