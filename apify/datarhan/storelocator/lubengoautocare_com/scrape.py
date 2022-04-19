from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(proxy_country="us", verify_ssl=True)
    start_url = "https://oilchangers.com/wp-admin/admin-ajax.php"
    domain = "lubengoautocare.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {"action": "get_all_stores", "lat": "", "lng": ""}
    data = session.post(start_url, headers=hdr, data=frm).json()
    for i, poi in data.items():
        location_name = poi["na"]
        if "coming soon" in location_name.lower():
            continue
        page_url = poi["gu"]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//div[@class="store_locator_single_opening_hours"]/text()')
        hoo = ", ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=poi["st"],
            city=poi["ct"],
            state=poi["rg"],
            zip_postal=poi["zp"],
            country_code="",
            store_number=poi["ID"],
            phone=poi.get("te"),
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
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
