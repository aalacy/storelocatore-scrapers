import re
import demjson
from lxml import etree
from time import sleep
from random import uniform

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "millersalehouse.com"
    start_url = "https://millersalehouse.com/locations/"
    hdr = {
        "X-Requested-With": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }

    hdr_loc = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, */*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "__RequestVerificationToken": "",
        "X-Requested-With": "XMLHttpRequest",
        "X-Olo-Request": "1",
        "X-Olo-Viewport": "Desktop",
        "X-Olo-App-Platform": "web",
        "X-Olo-Country": "us",
    }
    response = session.post(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "var locations")]/text()')[0]
    all_locations = re.findall(
        "var locations = (.+);", data.replace("\n", "").replace("\t", "")
    )[0]
    all_locations = re.sub(r"new google.maps.LatLng\((.+?)\),", '"\1",', all_locations)
    all_locations = demjson.decode(all_locations)
    for poi in all_locations:
        if "Coming Soon" in poi["name"]:
            continue
        poi_html = etree.HTML(poi["content"])
        raw_address = poi_html.xpath('//span[@class="address"]/text()')
        sleep(uniform(3, 10))
        poi_url = (
            f'https://order.millersalehouse.com/api/vendors/{poi["olo"].split("/")[-1]}'
        )
        poi_data = session.get(poi_url, headers=hdr_loc).json()
        passed = False
        while not passed:
            session = SgRequests(proxy_country="us")
            sleep(uniform(3, 10))
            poi_data = session.get(poi_url, headers=hdr_loc).json()
            passed = poi_data.get("vendor")

        hoo = []
        for e in poi_data["vendor"]["weeklySchedule"]["calendars"][0]["schedule"]:
            hoo.append(f'{e["weekDay"]} {e["description"]}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["olo"],
            location_name=poi["name"]
            .replace("&#8217", "'")
            .replace("&#8211; Now Open!", ""),
            street_address=poi["street"]
            .replace("<br>", " ")
            .replace(" Crossings Plaza", ""),
            city=raw_address[-1].split(", ")[0],
            state=raw_address[-1].split(", ")[-1].split()[0],
            zip_postal=poi["zip"],
            country_code="",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["coords"].split(",")[0],
            longitude=poi["coords"].split(",")[-1],
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
