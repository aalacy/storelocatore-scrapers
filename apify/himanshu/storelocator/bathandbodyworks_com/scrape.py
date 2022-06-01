# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_url = "https://www.bathandbodyworks.com/on/demandware.store/Sites-BathAndBodyWorks-Site/en_US/Stores-GetNearestStores?latitude=39.4923&longitude=-0.4046&countryCode=US&distanceUnit=mi&maxdistance=50000&BBW=1"
    domain = "bathandbodyworks.com"
    hdr = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "cookie": "_pxhd=A20RvZIXctJCBmUD1vmZRC6c4Iej1W/FHIHN48Im5jKK4HGE7gueulI/uB9bDaze0XGOcoJ7DzS3IsEmqHB1Uw==:vjLQwFfy8ZkI1aTfr8x0w2AtjcGpgmQ7ReOcLFr9sB0Uu1pVGTQW0XUAu4roZbBrW0V/DvgQx85EF/W74Ob21ttBs2y2FcuIk/EvwLa0pj8=; dwac_8ad49cb0e424b64ecf842fb2a5=SyzDJGCPg3_KQ6yfqKzt2ViJs9PhCSW4SBw%3D|dw-only|||USD|false|US%2FEastern|true; cqcid=abxc5qSH4FlK7HzC1LcdCgHXhm; cquid=||; sid=SyzDJGCPg3_KQ6yfqKzt2ViJs9PhCSW4SBw; dwanonymous_3ca1c1eaa8cb6f7cdb78c17b8163592f=abxc5qSH4FlK7HzC1LcdCgHXhm; __cq_dnt=0; dw_dnt=0; dwsid=T9rKprjsT5mutqHJCLnphlx_ulE5auleLOkOH037QTfgXdkMXWCxja0XAyrlSGLh_YnGspmyFvK3p_mKPujzcA==; optimizelyEndUserId=oeu1654081828598r0.7657302277775213; pxcts=71a6ece5-e19b-11ec-a7cd-6652656e4f65; _pxvid=6fc1e85c-e19b-11ec-983d-756c75534873; EmailSignupModalDismissal=true; collapsibleState=true; utag_main=v_id:01811ef5bf43000d7674663ba5ea05079002e07100838$_sn:1$_ss:1$_st:1654083630728$ses_id:1654081830728%3Bexp-session$_pn:1%3Bexp-session; CONSENTMGR=consent:false%7Cts:1654081831053; __cq_uuid=adad1c70-4b6b-11ec-be7f-a5d87894805b; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; cmTPSet=Y; _px3=29ee5f81d947a1fd2d9f20c915353eab3434f9ce1adc86150b6087f6956d5932:XRL/ENVpRM5K9VvoSGVG4XtJe8w3PpgZJ0CMpCwBsZYNb94sfZsuBrwnnphlgmRx7hlZoQcyRODeIAbxORLwCg==:1000:P6a3suU7WMcd58kKzbsaTYepIVY1x4DVO9mxdqO6DUtFqxauecSO5ckk45OypkhgHIc3aTrXsHtT871VpD0V4MdsXWDVQpGgujYea0ox0Tu9qr7TlS8SGRDmumdzqymOEdjUHOz93n/tckO4Wl4fcIaiDSd+UfNW9gGvoqLVRRyASotnGq1OduWVrt6LEIt8eKGVgfY5ubUaa82Gvv0c2g==",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    data = session.get(start_url, headers=hdr).json()
    for store_number, poi in data["stores"].items():
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        hoo = ""
        if poi["storeHours"]:
            hoo = etree.HTML(poi["storeHours"]).xpath("//text()")
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.bathandbodyworks.com/store-locator",
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["stateCode"],
            zip_postal=poi["postalCode"],
            country_code=poi["countryCode"],
            store_number=store_number,
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
        )

        yield item

    start_url = (
        "https://www.bathandbodyworks.com/north-america/global-locations-canada.html"
    )
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="store-location"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//p[@class="store-name"]/text()')[0]
        raw_address = poi_html.xpath('.//p[@class="location"]/text()')[0].split(", ")
        phone = poi_html.xpath("./p[4]/text()")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address="",
            city=raw_address[0],
            state=raw_address[1],
            zip_postal="",
            country_code="CA",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
