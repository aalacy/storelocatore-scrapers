import json
from lxml import etree
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("aldi-suisse_ch")
DOMAIN = "aldi-suisse.ch"
MISSING = SgRecord.MISSING
locator_url = "https://www.aldi-suisse.ch/filialen/de-CH/Start"
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}

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


def fetch_data():
    with SgRequests() as http:
        START = 0
        END = None
        for idx, start_url in enumerate(start_urls[START:END]):
            logger.info(f"[{idx}] Pulling the data from {start_url}")
            response = http.get(start_url, headers=headers)
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

                # Latitude and Longitude
                # locX and locY refer to longitude and latitude respectively
                latlng = poi_html.xpath(".//@data-json")[0]

                latlng = (
                    latlng.split("bcInformation")[0]
                    .rstrip('"')
                    .replace("\\", "")
                    .rstrip(",")
                    .lstrip('"')
                    + "}"
                )
                latlng = json.loads(latlng)
                latitude = latlng["locY"] or MISSING
                longitude = latlng["locX"] or MISSING

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
                    locator_domain=DOMAIN,
                    page_url=locator_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=MISSING,
                    zip_postal=zip_code,
                    country_code="",
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hoo,
                )

                yield item


def scrape():
    logger.info("Scrape Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)
    logger.info("Scrape Finished")


if __name__ == "__main__":
    scrape()
