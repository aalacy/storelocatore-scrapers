# -*- coding: utf-8 -*-
import re
import json
from lxml import etree
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium import SgFirefox
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_1_KM

logger = sglog.SgLogSetup().get_logger(logger_name="bipa.at")


def fetch_locations(session, url, latlng, retry=0):
    lat, lng = latlng

    try:

        html = session.execute_async_script(
            f"""
            fetch("{url}", {{
                "credentials": "include",
                "headers": {{
                    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-User": "?1"
                }},
                "referrer": "https://www.bipa.at/filialen",
                "body": "&latitude={lat}&longitude={lng}",
                "method": "POST",
                "mode": "cors"
            }})
            .then(res => res.text())
            .then(arguments[0])
        """
        )

        return html
    except:
        if retry < 3:
            return fetch_locations(session, url, latlng, retry + 1)


def fetch_data():
    domain = "bipa.at"

    search = DynamicGeoSearch(
        max_search_distance_miles=1,
        granularity=Grain_1_KM(),
        country_codes=[SearchableCountries.AUSTRIA],
    )

    with SgFirefox() as session:
        session.get("https://www.bipa.at/filialen")
        session.set_script_timeout(300)

        tree = etree.HTML(session.page_source)
        url = tree.xpath('//form[@id="frmStorelocator"]/@action')[0]

        for latlng in search:
            html = fetch_locations(session, url, latlng)

            dom = etree.HTML(html)

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
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
