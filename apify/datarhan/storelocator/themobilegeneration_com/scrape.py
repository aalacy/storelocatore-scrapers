from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://themobilegeneration.com/wp-json/wpgmza/v1/datatables/base64eJy1kruKwzAQRf9lahV5NurCFmk2xJBAIOtlmVgTW0SWzUg2Cyb-vmPHge3SxN1wde9Rczqoi-rDYQig4ZRsd+dNmu6Qb8SfNkTr8zTdmBZ9RuaIF0egIETkCHqmwJHPYwF6LXeJ9Y81QllIJatcU3phfnVgMOLQ9liSvPcEQs6KAacjN6SgYkP8P3hUQHfQomvGHVNOv6Cv6ALd7+rJnk-IXkzIXk7IXk3IXr+f-T3OBmMe9gzOGCsRYMigr7wGKbhaF4lF3AQZS1Gwk7BqidkaGp3e918dKPZ3eE7-AF9yA7Q"
    domain = "themobilegeneration.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    for poi in data["data"]:
        page_url = (
            "https://themobilegeneration.com/locations"
            + etree.HTML(poi[3]).xpath("//@href")[0]
        )
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_adr = poi[1].split(", ")
        zip_code = raw_adr[2].split()[-1]
        city = raw_adr[1]
        if len(zip_code) == 2:
            zip_code = loc_dom.xpath(
                '//strong[span[contains(text(), "Address")]]/following-sibling::span/text()'
            )[-1].split()[-1]
            if len(zip_code) == 3:
                zip_code = loc_dom.xpath(
                    '//span[contains(text(), "{}")]/text()'.format(city)
                )[-1].split()[-1]
        if poi[2] and "Please" not in poi[2]:
            poi_html = etree.HTML(poi[2])
            raw_data = poi_html.xpath("//text()")
            phone = raw_data[1]
        else:
            phone = loc_dom.xpath(
                '//strong[span[contains(text(), "Phone Number:")]]/following-sibling::span/text()'
            )[0]
        geo = (
            loc_dom.xpath('//iframe[@loading="lazy"]/@src')[0]
            .split("!2d")[-1]
            .split("!2m")[0]
            .split("!3d")
        )
        hoo = " ".join(raw_data).split("Hours:")[-1].strip()
        if loc_dom.xpath('//p[contains(text(), "TEMPORARILY CLOSED")]'):
            hoo = "TEMPORARILY CLOSED"
        str_2 = loc_dom.xpath(
            '//strong[span[contains(text(), "Address:")]]/following-sibling::span/text()'
        )
        street_address = raw_adr[0]
        if len(str_2) == 3:
            street_address += ", " + str_2[1].strip()

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi[0],
            street_address=street_address,
            city=city,
            state=raw_adr[2].split()[0],
            zip_postal=zip_code,
            country_code=raw_adr[-1],
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[-1].split("!")[0],
            longitude=geo[0],
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
