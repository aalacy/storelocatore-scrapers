from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://elriogrande.net/wp-admin/admin-ajax.php?action=store_search&lat=32.902532&lng=-96.706373&max_results=25&search_radius=50&autoload=1"
    domain = "elriogrande.net"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        page_url = f'https://elriogrande.net{poi["url"]}'
        loc_response = session.get(page_url, headers=hdr)
        phone = ""
        state = poi["state"]
        street_address = poi["address"]
        hoo = ""
        if loc_response.status_code == 200:
            loc_dom = etree.HTML(loc_response.text)
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else ""
            if not phone:
                phone = (
                    loc_dom.xpath(
                        '//h2[contains(text(), "Address")]/following-sibling::h4/text()'
                    )[-1]
                    .split(":")[-1]
                    .strip()
                )
            raw_address = loc_dom.xpath(
                '//h2[contains(text(), "Address")]/following-sibling::h4/text()'
            )
            raw_address = [
                e.strip() for e in raw_address if "Phone" not in e and "Fax" not in e
            ]
            if len(raw_address) == 3:
                raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
            if not state:
                state = raw_address[-1].split(", ")[-1].split()[0]
            street_address = raw_address[0]
            hoo = loc_dom.xpath(
                '//div[contains(text(), "Store")]/following-sibling::div[1]/text()'
            )[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["store"],
            street_address=street_address,
            city=poi["city"],
            state=state,
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=poi["id"],
            phone=phone,
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
