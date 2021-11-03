from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "costulessdirect.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
}


def fetch_data():

    search_url = "https://www.costulessdirect.com/resources/locations/"
    data = "page=1&rows=10000000&search=search&address=&radius=2000000"
    stores_req = session.post(search_url, headers=headers, data=data)
    stores_sel = lxml.html.fromstring(stores_req.text)
    lng_list = []
    lat_list = []
    script = stores_sel.xpath('//script[@type="text/javascript"]/text()')
    for j in script:
        if "var marcadores" in j:
            con = (
                j.split("var marcadores = [")[1]
                .split("//end marcadores")[0]
                .replace("];", "")
                .strip()[:-1]
            )
            for geo_loc in con.split("positionMarcadores:")[1:]:
                lat_list.append(
                    geo_loc.split("lat : ")[1]
                    .strip()
                    .split(",")[0]
                    .strip()
                    .replace("\t", "")
                )
                lng_list.append(
                    geo_loc.split("lng : ")[1]
                    .strip()
                    .split(",")[0]
                    .strip()
                    .replace("}", "")
                    .replace("\t", "")
                )

    stores = stores_sel.xpath('//div[@class="main_content"]')
    for index in range(0, len(stores)):
        page_url = "".join(stores[index].xpath('h2[@itemprop="name"]/a/@href')).strip()
        locator_domain = website
        location_name = "".join(
            stores[index].xpath('h2[@itemprop="name"]/a/text()')
        ).strip()

        street_address = "".join(
            stores[index].xpath(
                'div[@itemprop="address"]/p[@itemprop="streetAddress"]/text()'
            )
        ).strip()

        city = "".join(
            stores[index].xpath(
                'div[@itemprop="address"]/p/span[@itemprop="addressLocality"]/text()'
            )
        ).strip()
        state = "".join(
            stores[index].xpath(
                'div[@itemprop="address"]/p/span[@itemprop="addressRegion"]/text()'
            )
        ).strip()
        zip = "".join(
            stores[index].xpath(
                'div[@itemprop="address"]/p/span[@itemprop="postalCode"]/text()'
            )
        ).strip()

        phone = "".join(
            stores[index].xpath('p/span[@itemprop="telephone"]/text()')
        ).strip()

        log.info(page_url)
        hours_of_operation = ""
        if "#" not in page_url:
            page_res = session.get(page_url, headers=headers)
            page_sel = lxml.html.fromstring(page_res.text)
            hours = page_sel.xpath(
                '//div[@class="content_profile"]/div/p[@itemprop="openingHours"]/text()'
            )
            hours = list(filter(str, [x.strip() for x in hours]))
            hours_of_operation = "; ".join(hours).strip()

        else:
            page_url = SgRecord.MISSING

        latitude = lat_list[index]
        longitude = lng_list[index]

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
