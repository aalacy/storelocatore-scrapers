import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.benavides.com.mx/sucursales"
    domain = "benavides.com.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
    data = json.loads(data)

    all_locations = data["props"]["pageProps"]["maplocations"]
    for poi in all_locations:
        lv = f"Lu a Vi: {poi['Lu_vi_open']} a {poi['Lu_vi_close']}"
        sa = f"Sábado: {poi['Sa_open']} a {poi['Sa_close']}"
        do = f"DOMIRNGO {poi['Do_open']} a {poi['Do_close']}"
        hoo = f"{lv}, {sa}, {do}"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.benavides.com.mx/sucursales",
            location_name=poi["Branch_Name"],
            street_address=poi["Branch_Street"],
            city=poi["Branch_City"],
            state=poi["Branch_State"],
            zip_postal=poi["Branch_Zip"],
            country_code="",
            store_number=poi["Branch_Number"],
            phone="",
            location_type="",
            latitude=poi["Branch_Latitud"],
            longitude=poi["Branch_Longitude"],
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
