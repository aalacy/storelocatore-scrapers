from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.com.hk/Lexus-Showroom.aspx"
    domain = "lexus.com.hk"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "X-MicrosoftAjax": "Delta=true",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//select[@id="p_lt_ctl00_pageplaceholder_p_lt_ctl00_LexusFindOurCenter_plcUp_ddlCenter"]/option/@value'
    )[1:]
    for store_number in all_locations:
        token = dom.xpath('//input[@id="__CMSCsrfToken"]/@value')[0]
        viewstate = dom.xpath('//input[@id="__VIEWSTATE"]/@value')[0]

        frm = {
            "manScript": "p$lt$ctl00$pageplaceholder$p$lt$ctl00$LexusFindOurCenter$sys_pnlUpdate|p$lt$ctl00$pageplaceholder$p$lt$ctl00$LexusFindOurCenter$plcUp$ddlCenter",
            "__CMSCsrfToken": token,
            "__EVENTTARGET": "p$lt$ctl00$pageplaceholder$p$lt$ctl00$LexusFindOurCenter$plcUp$ddlCenter",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": viewstate,
            "lng": "en-GB",
            "__VIEWSTATEGENERATOR": "A5343185",
            "__SCROLLPOSITIONX": "0",
            "__SCROLLPOSITIONY": "0",
            "p$lt$ctl00$pageplaceholder$p$lt$ctl00$LexusFindOurCenter$plcUp$ddlCenterType": "Showroom",
            "p$lt$ctl00$pageplaceholder$p$lt$ctl00$LexusFindOurCenter$plcUp$ddlCenter": store_number,
            "p$lt$ctl00$LexusFooter$EmailAddress": "",
            "__ASYNCPOST": "true",
            "": "",
        }
        loc_response = session.post(start_url, data=frm, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//p[@id="pName"]/text()')[0]
        raw_address = loc_dom.xpath('//p[@id="pAddress"]/text()')[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = loc_dom.xpath('//div[@id="pPhone"]/text()')[0]
        hoo = loc_dom.xpath('//div[@id="pOpenHour"]/text()')[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="HK",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=raw_address,
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
