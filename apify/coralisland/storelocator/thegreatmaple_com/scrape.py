import re
from lxml import etree

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://thegreatmaple.com/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[@title="Locations"]/following-sibling::ul/li/a/@href'
    )
    for store_url in list(set(all_locations)):
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/strong/span/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//h3[strong[span[contains(text(), "ADDRESS")]]]/following-sibling::p/span/text()'
        )
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//h3[strong[span[contains(text(), "ADDRESS")]]]/following-sibling::p/text()'
            )
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//h4[span[strong[span[contains(text(), "ADDRESS")]]]]/following-sibling::p[1]/text()'
            )
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//h4[span[strong[contains(text(), "ADDRESS")]]]/following-sibling::p[1]/span/text()'
            )[1:]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = raw_address[-1]
        location_type = "<MISSING>"

        try:
            latitude = loc_dom.xpath("//div/@data-latitude")[0]
            longitude = loc_dom.xpath("//div/@data-longitude")[0]
        except:
            latitude = longitude = "<MISSING>"

        hoo = loc_dom.xpath(
            '//h3[strong[span[contains(text(), "HOURS")]]]/following-sibling::*//text()'
        )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h4[span[strong[span[contains(text(), "HOURS")]]]]/following-sibling::*//text()'
            )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h4[span[strong[contains(text(), "HOURS")]]]/following-sibling::*//text()'
            )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).split(" Hours subject")[0].split("Pickup: ")[-1]
            if hoo
            else "<MISSING>"
        )

        sgw.write_row(
            SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
