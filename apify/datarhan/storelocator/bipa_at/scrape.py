# -*- coding: utf-8 -*-
import re
import json
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, DynamicZipAndGeoSearch, SearchableCountries


def fetch_data():
    start_url = "https://www.bipa.at/filialen?dwcont=C1344944564"
    domain = "bipa.at"

    search = DynamicZipAndGeoSearch(
        expected_search_radius_miles=1,
        max_search_distance_miles=1,
        country_codes=[SearchableCountries.AUSTRIA],
    )

    with SgRequests() as session:
        headers = {
            "Host": "www.bipa.at",
            "Cookie": "dwsid=g-bfHLgGgRTX4rp9CDtWJUsAqCuiA7nk6kMHWOFpx3afRx43SdhAVLQhACRPFJHEvAiLTAkV79LGYBYSKYRAKg==;",
        }
        session.get("https://www.bipa.at/filialen")
        for code, (lat, lng) in search:
            data = {
                "dwfrm_storelocator_zipcity": code,
                "latitude": str(lat),
                "longitude": str(lng),
            }
            response = session.post(start_url, data=data, headers=headers)
            dom = etree.HTML(response.text)

            all_locations = dom.xpath("//@data-options")
            for poi in all_locations:
                poi = poi.replace("null", '""')
                if poi.startswith("["):
                    continue
                if len(poi.strip()) < 10:
                    continue
                location_name = re.findall(r'name":"(.+?)",', poi)[0]
                page_url = "https://www.bipa.at/filialen"
                street_address = re.findall(r'address1":"(.+?)",', poi)[0]
                city = re.findall(r'city":"(.+?)",', poi)[0]
                state = re.findall(r'stateCode":"(.+?)",', poi)[0]
                zip_code = re.findall(r'postalCode":"(.+?)",', poi)[0]
                phone = re.findall(r'phone":"(.+?)",', poi)[0]
                hoo = re.findall(r'storeHours":"(.+?\})"', poi)[0].replace("\\", "")
                hoo = json.loads(hoo)
                hours = []
                for d, h in hoo.items():
                    if h:
                        hours.append(f"{d}: {h[0]}")
                    else:
                        hours.append(f"{d}: closed")
                hours = ", ".join(hours)
                store_number = re.findall('storeid":"(.+?)"', poi)[0]
                latitude = re.findall('latitude":(.+?),', poi)[0]
                longitude = re.findall('longitude":(.+?),', poi)[0]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code="AT",
                    store_number=store_number,
                    phone=phone,
                    location_type="",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours,
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
