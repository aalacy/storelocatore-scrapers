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

    start_urls = [
        "https://www.intersport.es/tiendas",
        "https://www.intersport.at/stores",
        "https://www.intersport.cz/stores",
        "https://www.intersport.hu/stores",
        "https://www.intersport.nl/stores",
        "https://www.intersport.no/stores",
        "https://www.intersport.ch/de/stores",
    ]
    domain = "intersport.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for start_url in start_urls:
        response = session.get(start_url, headers=hdr)
        dom = etree.HTML(response.text)
        data = (
            dom.xpath('//script[contains(text(), "storesJson = ")]/text()')[0]
            .split("Json =")[-1]
            .strip()[:-1]
        )

        all_locations = json.loads(data)
        for poi in all_locations:
            if ".ch" in start_url:
                page_url = (
                    f'https://www.intersport.ch/de/storedetail?storeID={poi["storeID"]}'
                )
            else:
                page_url = f'https://{start_url.split("/")[2]}/storedetail?storeID={poi["storeID"]}'
            loc_response = session.get(page_url)
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)
            street_address = loc_dom.xpath('//div[@itemprop="streetAddress"]/text()')[
                0
            ].strip()
            if not street_address:
                continue
            hoo = []
            days = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            for day in days:
                if poi["storeHours"]:
                    if poi["storeHours"].get(day):
                        opens = poi["storeHours"][day]["fromFirst"]
                        if opens == "CERRADO":
                            hoo.append(f"{day}: {opens}")
                        else:
                            if poi["storeHours"][day].get("fromSecond"):
                                opens = f"{poi['storeHours'][day]['fromFirst']} - {poi['storeHours'][day]['toFirst']}"
                                opens_2 = f"{poi['storeHours'][day]['fromSecond']} - {poi['storeHours'][day]['toSecond']}"
                                hoo.append(f"{day}: {opens} {opens_2}")
                            else:
                                opens = f"{poi['storeHours'][day]['fromFirst']} - {poi['storeHours'][day]['toFirst']}"
                                hoo.append(f"{day}: {opens}")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=street_address,
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi.get("postalCode"),
                country_code=poi["countryCode"],
                store_number=poi["storeID"],
                phone=poi.get("phone"),
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.COUNTRY_CODE, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
