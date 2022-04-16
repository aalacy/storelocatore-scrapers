import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://maxemhealthurgentcare.com/locations-2/"
    domain = "maxemhealthurgentcare.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li/a[contains(@href, "locations-2")]/@href')
    for store_url in list(set(all_locations)):
        if store_url == "https://maxemhealthurgentcare.com/locations-2/":
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        data = (
            loc_dom.xpath('//script[contains(text(), "map_options")]/text()')[0]
            .split("maps(")[-1]
            .split(").data")[0]
        )
        data = json.loads(data)
        poi = data["places"][0]

        phone = loc_dom.xpath('//span[contains(text(), "Ph.")]/text()')
        if phone:
            phone = phone[0].replace("Ph. ", "")
        if not phone:
            phone = loc_dom.xpath('//span[contains(text(), "Ph:")]/text()')
            if phone:
                phone = phone[0].replace("Ph: ", "")
        if not phone:
            phone = loc_dom.xpath("//h1/following-sibling::p[1]/span/text()")
            phone = [e.strip() for e in phone if "Ph." in e]
            phone = phone[0].replace("Ph. ", "") if phone else SgRecord.MISSING
        hoo = loc_dom.xpath(
            '//h3[contains(text(), "Hours of Operation")]/following-sibling::p//text()'
        )
        hoo = [e.replace("\xa0", "").strip() for e in hoo]
        hours_of_operation = " ".join(hoo)
        state = poi["location"]["state"]
        zip_code = poi["location"]["postal_code"]
        if zip_code == "70460":
            state = "LA"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=poi["title"],
            street_address=poi["address"].split(",")[0],
            city=poi["location"]["city"],
            state=state,
            zip_postal=zip_code,
            country_code=poi["location"]["country"],
            store_number="",
            phone=phone.replace("Ph: ", ""),
            location_type=SgRecord.MISSING,
            latitude=poi["location"]["lat"],
            longitude=poi["location"]["lng"],
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
