# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://serendipitylabs.com/us/"
    domain = "serendipitylabs.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[contains(@class, "row location")]//a/@href')
    all_locations += dom.xpath(
        '//a[contains(text(), "Locations")]/following-sibling::div//a/@href'
    )[:-1]
    for page_url in list(set(all_locations)):
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        data = loc_dom.xpath('//script[@class="yoast-schema-graph"]/text()')[0]
        data = json.loads(data)
        poi_adr = [e for e in data["@graph"] if e["@type"] == "PostalAddress"]
        if poi_adr:
            poi_adr = poi_adr[0]
            poi = [e for e in data["@graph"] if "Place" in e["@type"]][0]
            hoo = []
            for e in poi["openingHoursSpecification"]:
                for day in e["dayOfWeek"]:
                    hoo.append(f'{day}: {e["opens"]} - {e["closes"]}')
            hoo = ", ".join(hoo).replace("00:00 - 00:00", "closed")
            location_name = poi["name"].replace("&#8211;", "-")
            street_address = poi_adr["streetAddress"]
            city = poi_adr["addressLocality"]
            state = poi_adr["addressRegion"]
            zip_code = poi_adr["postalCode"]
            country_code = poi_adr["addressCountry"]
            phone = poi["telephone"][0]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
        else:
            data = loc_dom.xpath('//script[contains(text(), "locations = ")]/text()')[
                0
            ].split("locations = ")[-1][:-1]
            data = json.loads(data)
            hoo = ""
            location_name = loc_dom.xpath("//h1/text()")[0]
            street_address = data[0][4]
            city = data[0][5].split(", ")[0]
            state = ""
            zip_code = data[0][5].split(", ")[-1].replace("England", "")
            country_code = data[0][5].split(", ")[-1].split()[0]
            phone = data[0][6]
            latitude = data[0][1]
            longitude = data[0][2]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
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
