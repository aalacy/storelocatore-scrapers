import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://classiccollision.net/wp-admin/admin-ajax.php?action=store_search&lat=33.749&lng=-84.38798&max_results=50&search_radius=1000&autoload=1"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        page_url = poi["permalink"]
        location_name = poi["store"].replace("&#8211;", "-")
        street_address = poi["address"]
        if "USA" in street_address:
            street_address = street_address.split(",")[0]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zip"]
        country_code = poi["country"]
        store_number = poi["id"]
        phone = poi["phone"].split("(c")[0]
        if not phone:
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            phone = loc_dom.xpath('//span[@class="tel"]/text()')
            if not phone:
                phone = loc_dom.xpath('//a[@class="tel"]/span/text()')
            phone = phone[0]
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = etree.HTML(poi["hours"]).xpath("//text()")
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
