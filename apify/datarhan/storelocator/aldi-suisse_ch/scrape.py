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
        "https://www.yellowmap.de/Presentation/AldiSued/de-CH/ResultList?callback=jQuery203048548467729689415_1630659526129&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=8.47869873046875&Luy=47.81315451752768&Rlx=10.12115478515625&Rly=46.65697731621612&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIWC=false&Filters.ASxFIPA=false&Filters.ASxFIBA=false&Filters.ASxFIRE=false&Filters.ASxFIEL=false&Filters.ASxKAFE=false&_=1630659526151",
        "https://www.yellowmap.de/Presentation/AldiSued/de-CH/ResultList?callback=jQuery203048548467729689415_1630659526129&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=7.3333740234375&Luy=47.864773955792245&Rlx=8.975830078125&Rly=46.70973594407157&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIWC=false&Filters.ASxFIPA=false&Filters.ASxFIBA=false&Filters.ASxFIRE=false&Filters.ASxFIEL=false&Filters.ASxKAFE=false&_=1630659526153",
        "https://www.yellowmap.de/Presentation/AldiSued/de-CH/ResultList?callback=jQuery203048548467729689415_1630659526129&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=6.30889892578125&Luy=47.61727271567975&Rlx=7.95135498046875&Rly=46.45678142812658&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIWC=false&Filters.ASxFIPA=false&Filters.ASxFIBA=false&Filters.ASxFIRE=false&Filters.ASxFIEL=false&Filters.ASxKAFE=false&_=1630659526155",
        "https://www.yellowmap.de/Presentation/AldiSued/de-CH/ResultList?callback=jQuery203048548467729689415_1630659526129&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=5.9710693359375&Luy=46.74927110475196&Rlx=7.613525390625&Rly=45.569832358492825&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIWC=false&Filters.ASxFIPA=false&Filters.ASxFIBA=false&Filters.ASxFIRE=false&Filters.ASxFIEL=false&Filters.ASxKAFE=false&_=1630659526157",
        "https://www.yellowmap.de/Presentation/AldiSued/de-CH/ResultList?callback=jQuery203048548467729689415_1630659526129&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=6.7401123046875&Luy=46.67205646734499&Rlx=8.382568359375&Rly=45.49094569262732&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIWC=false&Filters.ASxFIPA=false&Filters.ASxFIBA=false&Filters.ASxFIRE=false&Filters.ASxFIEL=false&Filters.ASxKAFE=false&_=1630659526159",
        "https://www.yellowmap.de/Presentation/AldiSued/de-CH/ResultList?callback=jQuery203048548467729689415_1630659526129&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=7.29766845703125&Luy=47.2512713278804&Rlx=8.94012451171875&Rly=46.08275685027116&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIWC=false&Filters.ASxFIPA=false&Filters.ASxFIBA=false&Filters.ASxFIRE=false&Filters.ASxFIEL=false&Filters.ASxKAFE=false&_=1630659526161",
        "https://www.yellowmap.de/Presentation/AldiSued/de-CH/ResultList?callback=jQuery203048548467729689415_1630659526129&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=8.18756103515625&Luy=47.13929295458033&Rlx=9.83001708984375&Rly=45.9683336020637&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIWC=false&Filters.ASxFIPA=false&Filters.ASxFIBA=false&Filters.ASxFIRE=false&Filters.ASxFIEL=false&Filters.ASxKAFE=false&_=1630659526163",
        "https://www.yellowmap.de/Presentation/AldiSued/de-CH/ResultList?callback=jQuery203048548467729689415_1630659526129&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=9.2010498046875&Luy=47.40392636603371&Rlx=10.843505859375&Rly=46.238752301105684&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIWC=false&Filters.ASxFIPA=false&Filters.ASxFIBA=false&Filters.ASxFIRE=false&Filters.ASxFIEL=false&Filters.ASxKAFE=false&_=1630659526165",
        "https://www.yellowmap.de/Presentation/AldiSued/de-CH/ResultList?callback=jQuery203048548467729689415_1630659526129&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=7.6190185546875&Luy=47.62097541515849&Rlx=9.261474609375&Rly=46.4605655457854&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIWC=false&Filters.ASxFIPA=false&Filters.ASxFIBA=false&Filters.ASxFIRE=false&Filters.ASxFIEL=false&Filters.ASxKAFE=false&_=1630659526167",
    ]
    domain = "aldi-suisse.ch"

    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//li[contains(@class, "resultItem")]')
        for poi_html in all_locations:
            location_name = poi_html.xpath(".//strong/text()")[0]
            street_address = poi_html.xpath(
                './/div[contains(@itemprop, "streetAddress")]/text()'
            )[0]
            city = poi_html.xpath(".//@data-city")[0].replace('\\"', "")
            zip_code = (
                poi_html.xpath(".//div[@data-city]/text()")[0]
                .replace('\\"', "")
                .split(city)[0]
                .strip()
            )
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
            phone = phone[0].replace("\\r\\n", "").strip() if phone else ""
            latlng = dom.xpath(".//@data-json")[0]

            latlng = (
                latlng.split("bcInformation")[0]
                .rstrip('"')
                .replace("\\", "")
                .rstrip(",")
                .lstrip('"')
                + "}"
            )
            latlng = json.loads(latlng)
            latitude = latlng["locY"] or SgRecord.MISSING
            longitude = latlng["locX"] or SgRecord.MISSING

            hoo = poi_html.xpath(
                './/table[contains(@class, "openingHoursTable")]//text()'
            )
            hoo = " ".join(
                [
                    e.replace("\\r\\n", "").strip()
                    for e in hoo
                    if e.replace("\\r\\n", "").strip()
                ]
            )

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.aldi-suisse.ch/filialen/de-CH/Start",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=zip_code,
                country_code="",
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
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
