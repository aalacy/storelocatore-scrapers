from sglogging import sglog
from sgrequests import SgRequests, SgRequestError
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
import json

session = SgRequests()
website = "desigual_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://desigual.com"
MISSING = SgRecord.MISSING


def fetch_data():
    countries_req = session.get("https://www.desigual.com/", headers=headers)
    countries_sel = lxml.html.fromstring(countries_req.text)

    country_list = countries_sel.xpath(
        '//select[@name="countrySelector"]/option/@data-locale'
    )
    for country in country_list:
        country_url = (
            "https://www.desigual.com/"
            + country
            + "/shops/?showMap=true&horizontalView=true&isForm=true"
        )
        log.info(country_url)
        stores_req = session.get(country_url, headers=headers)
        if isinstance(stores_req, SgRequestError):
            log.error(f"countryURL ERROR: {country_url}")
            country_url = country_url.replace("/shops/", "/tiendas/")
            stores_req = session.get(country_url, headers=headers)

        stores_sel = lxml.html.fromstring(stores_req.text)
        loclist = stores_sel.xpath('//ul[@id="collapseExample"]/li')
        for loc in loclist:
            if "(1)" in "".join(loc.xpath("a/text()")).strip():
                page_url = "".join(loc.xpath("a/@href")).strip()
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_json = json.loads(
                    store_req.text.split('initial-stores="')[1]
                    .split('">')[0]
                    .replace("&quot;", '"')
                )["stores"][0]
                store_number = store_json["storeId"]
                location_name = store_json["name"].strip()
                street_address = store_json["address"].strip()
                city = store_json.get("city", MISSING)
                state = store_json.get("region", MISSING)
                zip_postal = store_json.get("postalCode", MISSING)
                country_code = store_json.get("countryCode", MISSING)
                latitude = store_json.get("latitude", MISSING)
                longitude = store_json.get("longitude", MISSING)
                phone = store_json.get("phone", MISSING)
                hours = store_json["schedule"]
                hours_list = []
                if hours:
                    for hour in hours:
                        day = hour["name"]
                        if hour["isOpen"] is True:
                            time = hour["value"]
                        else:
                            time = "Closed"
                        hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            else:
                cities_url = "".join(loc.xpath("a/@href")).strip()
                log.info(f"cities_URL: {cities_url}")
                stores_req = session.get(cities_url, headers=headers)
                stores_sel = lxml.html.fromstring(stores_req.text)
                loclist = stores_sel.xpath('//ul[@id="collapseExample"]/li')
                for loc in loclist:
                    page_url = "".join(loc.xpath("a/@href")).strip()
                    log.info(page_url)
                    store_req = session.get(page_url, headers=headers)
                    store_json = json.loads(
                        store_req.text.split('initial-stores="')[1]
                        .split('">')[0]
                        .replace("&quot;", '"')
                    )["stores"][0]
                    store_number = store_json["storeId"]
                    location_name = store_json["name"].strip()
                    street_address = store_json["address"].strip()
                    city = store_json.get("city", MISSING)
                    state = store_json.get("region", MISSING)
                    zip_postal = store_json.get("postalCode", MISSING)
                    country_code = store_json.get("countryCode", MISSING)
                    latitude = store_json.get("latitude", MISSING)
                    longitude = store_json.get("longitude", MISSING)
                    phone = store_json.get("phone", MISSING)
                    hours = store_json["schedule"]
                    hours_list = []
                    if hours:
                        for hour in hours:
                            day = hour["name"]
                            if hour["isOpen"] is True:
                                time = hour["value"]
                            else:
                                time = "Closed"
                            hours_list.append(day + ":" + time)

                    hours_of_operation = "; ".join(hours_list).strip()

                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_postal,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=MISSING,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
