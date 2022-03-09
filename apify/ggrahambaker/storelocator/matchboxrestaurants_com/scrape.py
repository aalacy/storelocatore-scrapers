# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.matchboxrestaurants.com/home-locations"
    domain = "matchboxrestaurants.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_states = dom.xpath(
        '//div[@class="row sqs-row"]/div[@class="col sqs-col-2 span-2"]'
    )[:3]
    for state_html in all_states:
        all_locations = state_html.xpath(".//p/strong")
        for poi_html in all_locations:
            if not poi_html.xpath(".//text()"):
                continue
            location_name = poi_html.xpath(".//text()")
            if not location_name:
                continue
            if len(location_name) == 2:
                state = location_name[0]
                location_name = location_name[-1]
            else:
                location_name = location_name[0]
            raw_data = poi_html.xpath(".//following::text()")
            clear_data = []
            for e in raw_data:
                if not e.strip():
                    continue
                clear_data.append(e)
                if "order online" in e:
                    break
            clear_data = [e.strip() for e in clear_data if "now open" not in e][:-1]
            if "coming soon!" in clear_data:
                continue
            if len(clear_data) == 3:
                location_name = clear_data[0]
                clear_data = clear_data[1:]
            city = location_name
            zip_code = ""
            if "suite" in clear_data[1]:
                state = clear_data[2].split(", ")[-1].split()[0]
                zip_code = clear_data[2].split(", ")[-1].split()[-1]
                city = clear_data[2].split(", ")[0]
                clear_data = [", ".join(clear_data[:2])] + [clear_data[3]]

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_name,
                street_address=clear_data[0],
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
                store_number="",
                phone=clear_data[1],
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
