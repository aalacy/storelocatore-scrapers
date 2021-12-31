import json
from time import sleep
from lxml import etree

from sgrequests import SgRequests
from sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "chanellospizza.com"
    start_url = "https://chanellospizza.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    city_dict = {}
    all_cities = dom.xpath('//div[@class="area-location"]')
    for city in all_cities:
        city_name = city.xpath(".//h1/text()")[0]
        loc_names = city.xpath('.//div[@class="location-item"]/strong/text()')
        for loc_name in loc_names:
            city_dict[loc_name.replace("’s", "s")] = city_name

    data = dom.xpath('//div[@class="map"]/@data-markers')[0]
    data = json.loads(data)

    for poi in data:
        poi_html = etree.HTML(poi["popup"])

        store_url = poi_html.xpath('.//div[@class="online-order"]/a/@href')[0]
        location_name = poi["title"].replace("&#8217;", "")
        street_address = poi_html.xpath(".//address/text()")
        street_address = street_address[0] if street_address else "<MISSING>"
        city = city_dict[location_name]
        state = "<MISSING>"
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        if "chanellospizza.com" in store_url:
            with SgFirefox() as driver:
                new_url = store_url.replace(
                    "#content=/Menu/ViewMenu/", "Menu.aspx?T=t&RestaurantID="
                )
                driver.get(new_url)
                sleep(5)
                loc_dom = etree.HTML(driver.page_source)

            check = loc_dom.xpath('.//div[@class="title"]/h1/text()')[0]
            if "online ordering" in check.lower():
                continue
            raw_data = loc_dom.xpath('//div[@class="sidebarSelectedLocation"]/p/text()')
            raw_data = [elem.strip() for elem in raw_data]
            if len(raw_data) == 4:
                raw_data = [", ".join(raw_data[:2])] + raw_data[2:]
            if len(raw_data) > 1:
                raw_data = raw_data[1].strip().split(", ")[-1].split()
                state = raw_data[0]
                zip_code = raw_data[1]
            else:
                raw_data = loc_dom.xpath(
                    '//p[contains(text(), "We are sorry for any inconvenience")]/following-sibling::p/text()'
                )[1:-1]
                addr = parse_address_intl(" ".join(raw_data))
                state = addr.state
                state = state if state else "<MISSING>"
                zip_code = zip_code if zip_code else "<MISSING>"
        if "foodtecsolutions" in store_url:
            with SgFirefox() as driver:
                driver.get(store_url)
                sleep(10)
                loc_dom = etree.HTML(driver.page_source)
                raw_data = loc_dom.xpath(
                    '//div[contains(@class, "store text-right")]/span/text()'
                )
                if raw_data:
                    raw_data = raw_data[0].split(", ")
                    street_address = raw_data[0]
                    city = raw_data[1]
                    state = raw_data[-1].split()[0]
                    zip_code = raw_data[-1].split()[-1]
        store_number = poi["id"]
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/@href')
        phone = phone[0].split(":")[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"][0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["location"][-1]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi_html.xpath('.//ul[@class="working-hours"]/li/text()')
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        if "intouchposonline" in store_url:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            raw_data = (
                loc_dom.xpath('//ul[@class="when"]/li[1]/span/text()')[1]
                .split("/")[-1]
                .strip()
                .split(", ")
            )
            street_address = raw_data[0]
            city = raw_data[1]
            state = raw_data[-1].split()[0]
            zip_code = raw_data[-1].split()[-1]
            hours_of_operation = (
                loc_dom.xpath('//span[contains(text(), "Hours:")]/text()')[-1]
                .replace("Hours: ", "")
                .replace("|", ",")
            )
        if "slicelife" in store_url:
            state = store_url.split("/")[4]
            zip_code = store_url.split("/")[6]

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
