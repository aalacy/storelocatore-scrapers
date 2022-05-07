from sglogging import sglog
from sgrequests import SgRequests, SgRequestError
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
import json
import html

session = SgRequests()
website = "desigual_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://desigual.com"
MISSING = SgRecord.MISSING


def encode_string(data_field):
    if data_field:
        return html.unescape(str(data_field))
    else:
        return data_field


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
        try:
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
                    if latitude == "0" or latitude == 0:
                        latitude, longitude = "<MISSING>", "<MISSING>"
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
                        location_name=encode_string(location_name),
                        street_address=encode_string(street_address),
                        city=encode_string(city),
                        state=encode_string(state),
                        zip_postal=encode_string(zip_postal),
                        country_code=encode_string(country_code),
                        store_number=encode_string(store_number),
                        phone=encode_string(phone),
                        location_type=MISSING,
                        latitude=encode_string(latitude),
                        longitude=encode_string(longitude),
                        hours_of_operation=encode_string(hours_of_operation),
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
                        if latitude == "0" or latitude == 0:
                            latitude, longitude = "<MISSING>", "<MISSING>"
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
                            location_name=encode_string(location_name),
                            street_address=encode_string(street_address),
                            city=encode_string(city),
                            state=encode_string(state),
                            zip_postal=encode_string(zip_postal),
                            country_code=encode_string(country_code),
                            store_number=encode_string(store_number),
                            phone=encode_string(phone),
                            location_type=MISSING,
                            latitude=encode_string(latitude),
                            longitude=encode_string(longitude),
                            hours_of_operation=encode_string(hours_of_operation),
                        )
        except:
            r = session.get(
                "https://www.desigual.com/on/demandware.store/Sites-dsglfranchise_hr-Site/it_IT/Address-SearchStoreAddress?longitude=15.9644&latitude=45.8071&deliveryPoint=STORE&radius=21&showOfficialStores=false&showOutlets=false&showAuthorized=false&showOnlyAllowDevosStores=false",
                headers=headers,
            )
            js = r.json()["shippingAddresses"]
            for j in js:

                page_url = j.get("detailUrl") or "<MISSING>"
                location_name = j.get("name") or "<MISSING>"
                street_address = j.get("address")
                city = j.get("city") or "<MISSING>"
                country_code = j.get("countryName") or "<MISSING>"
                zip_postal = j.get("postalCode") or "<MISSING>"
                latitude = j.get("latitude") or "<MISSING>"
                longitude = j.get("longitude") or "<MISSING>"
                if latitude == "0" or latitude == 0:
                    latitude, longitude = "<MISSING>", "<MISSING>"
                phone = j.get("phone") or "<MISSING>"
                state = "<MISSING>"
                hours_of_operation = "<MISSING>"
                store_number = j.get("id")
                hours = j.get("schedule")
                tmp = []
                if hours:
                    for h in hours:
                        day = h.get("name")
                        opens = h.get("open")
                        closes = h.get("close")
                        line = f"{day} {opens} - {closes}"
                        tmp.append(line)
                    hours_of_operation = "; ".join(tmp)

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=encode_string(location_name),
                    street_address=encode_string(street_address),
                    city=encode_string(city),
                    state=encode_string(state),
                    zip_postal=encode_string(zip_postal),
                    country_code=encode_string(country_code),
                    store_number=encode_string(store_number),
                    phone=encode_string(phone),
                    location_type=MISSING,
                    latitude=encode_string(latitude),
                    longitude=encode_string(longitude),
                    hours_of_operation=encode_string(hours_of_operation),
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
