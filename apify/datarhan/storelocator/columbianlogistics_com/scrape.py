import re
from lxml import etree
from pyjsparser import PyJsParser

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.columbianlogistics.com/warehousing/3pl-warehousing/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    parser = PyJsParser()
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_poi = dom.xpath('//div[@class="right-list"]/p/strong')
    map_id = dom.xpath("//iframe/@src")[0].split("mid=")[-1].split("&z")[0]
    response = session.get("https://www.google.com/maps/d/edit?hl=ja&mid=" + map_id)
    dom = etree.HTML(response.text)
    script = dom.xpath("//script/text()")[0]
    js = parser.parse(script)
    pagedata = js["body"][1]["declarations"][0]["init"]["value"]

    data = pagedata.replace("true", "True")
    data = data.replace("false", "False")
    data = data.replace("null", "None")
    data = data.replace("\n", "")
    data = eval(data)

    all_locations = data[1][6][0][12][0][13][0]
    for poi_html in all_poi:
        store_url = start_url
        location_name = poi_html.xpath("text()")[0].strip()
        if not location_name:
            continue
        raw_address = poi_html.xpath(".//following::text()")[1]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        phone = "<INACCESSIBLE>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        geo = []
        for poi in all_locations:
            poi_name = poi[5][0][1][0].split("-")[-1].strip()
            if location_name == poi_name:
                geo = poi[1][0][0]
            elif poi_name.split("&")[0] in location_name:
                geo = poi[1][0][0]
            if location_name == "Corporate Office & Grandville Distribution Center":
                geo = ["42.912088", "-85.73624000000001"]
            if geo:
                latitude = geo[0]
                longitude = geo[1]
        hours_of_operation = "<MISSING>"

        item = SgRecord(
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
