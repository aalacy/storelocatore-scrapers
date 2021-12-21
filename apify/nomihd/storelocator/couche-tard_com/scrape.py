import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("couche-tard_com")
session = SgRequests()


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    found_poi = []
    locator_domain = "couche-tard.com"
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    cont = True
    page = -1
    while cont:
        try:
            page += 1

            location_url = "https://www.couche-tard.com/stores_new.php?lat={}&lng={}&distance=9999999999&services=&region=quebec&page={}"
            stores = session.get(
                location_url.format("43.653482", "-79.383935", str(page)),
                headers=headers,
            ).json()["stores"]
            if len(stores) <= 0:
                cont = False
                break
            logger.info(f"visiting pageno:{page}")
            for key in stores.keys():
                if stores[key]["country"].upper() in ["CA", "CANADA"]:
                    if (
                        stores[key]["display_brand"] == "Couche-Tard"
                        and stores[key]["op_status"] != "Planned"
                        and stores[key]["op_status"] != "Future"
                    ):
                        page_url = "https://www.couche-tard.com" + stores[key]["url"]
                        if page_url in found_poi:
                            continue
                        found_poi.append(page_url)

                        page_url = page_url.replace(
                            "store-locator", "trouvez-votre-magasin"
                        ).strip()
                        logger.info(page_url)
                        try:
                            store_req = session.get(page_url, headers=headers)
                        except:
                            continue
                        store_sel = lxml.html.fromstring(store_req.text)
                        json_list = store_sel.xpath(
                            '//script[@type="application/ld+json"]/text()'
                        )
                        for js in json_list:
                            if "ConvenienceStore" in js:
                                store_json = json.loads(js)
                                location_name = stores[key]["display_brand"].replace(
                                    "&#039;", "'"
                                )
                                if stores[key]["franchise"] == "1":
                                    location_type = "Dealer/Distributor/Retail Partner"

                                else:
                                    location_type = "Brand Store"

                                phone = store_json["telephone"]
                                street_address = (
                                    store_json["address"]["streetAddress"]
                                    .replace("  ", " ")
                                    .replace("r&#039;", "'")
                                    .replace("&amp;", "&")
                                    .strip()
                                    .replace("&#039;", "'")
                                    .strip()
                                )
                                if street_address[-1:] == ",":
                                    street_address = street_address[:-1]
                                city = (
                                    store_json["address"]["addressLocality"]
                                    .strip()
                                    .replace("&#039;", "'")
                                )

                                state = "<MISSING>"
                                zipp = store_json["address"]["postalCode"].strip()
                                country_code = stores[key]["country"]
                                latitude = store_json["geo"]["latitude"]
                                longitude = store_json["geo"]["longitude"]
                                store_number = stores[key]["cost_center"]
                                hours = store_sel.xpath(
                                    '//div[@class="columns large-12 middle hours-wrapper"]/div[contains(@class,"hours-item")]'
                                )
                                hours_list = []
                                for hour in hours:
                                    day = "".join(hour.xpath("span[1]/text()")).strip()
                                    time = "".join(hour.xpath("span[2]/text()")).strip()
                                    hours_list.append(day + ":" + time)

                                hours_of_operation = "; ".join(hours_list).strip()

                                yield SgRecord(
                                    locator_domain=locator_domain,
                                    page_url=page_url,
                                    location_name=location_name,
                                    street_address=street_address,
                                    city=city,
                                    state=state,
                                    zip_postal=zipp,
                                    country_code=country_code,
                                    store_number=store_number,
                                    phone=phone,
                                    location_type=location_type,
                                    latitude=latitude,
                                    longitude=longitude,
                                    hours_of_operation=hours_of_operation,
                                )

        except Exception:
            cont = False


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
