from bs4 import BeautifulSoup
from sgrequests import SgRequests
from lxml import etree
import time
from random import randint
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = sglog.SgLogSetup().get_logger(logger_name="blomedry.com")


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    while True:
        if item[-1:] == " ":
            item = item[:-1]
        else:
            break
    return item.replace("\u2013", "-").strip()


def get_value(item):
    if item is None:
        item = "<MISSING>"
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    countries = ["US", "CA", "PH"]
    with SgRequests() as session:
        for country in countries:
            url = "https://blomedry.com/locations/?country=" + country
            request = session.get(url, headers=headers)
            time.sleep(randint(2, 4))
            response = etree.HTML(request.text)
            store_list = response.xpath('//li[contains(@class, "article-location")]')
            log.info(url)
            for i, store in enumerate(store_list):
                detail_url = store.xpath(".//h2/a/@href")[0]
                latitude = store.xpath("@data-lat")[0]
                longitude = store.xpath("@data-lng")[0]

                title = store.xpath(".//h2/a/text()")[0]
                address = store.xpath(".//p/text()")
                if country == "PH":
                    street_address = address[0].strip()
                    city = address[1].strip().split(",")[0].strip()
                    state = "<MISSING>"
                    zipcode = "<MISSING>"
                else:
                    if not address[-1].strip():
                        address.pop(-1)
                    try:
                        street_address = (
                            get_value(address[-3]).replace(",", " ").strip()
                            + " "
                            + get_value(address[-2]).replace(",", " ").strip()
                        )
                    except:
                        street_address = (
                            get_value(address[-2]).replace(",", " ").strip()
                        )
                    city_state = validate(address[-1])
                    city = city_state.split(",")[0]
                    if country == "US":
                        state = city_state.split(",")[1][:-6].strip()
                    else:
                        state = city_state.split(",")[1][:-7].strip()
                    if country == "US":
                        zipcode = city_state.split(",")[1][-6:].strip()
                        if zipcode == "90595" and city == "Torrance":
                            zipcode = "90505"
                    else:
                        zipcode = city_state.split(",")[1][-7:].strip()

                phone = "<MISSING>"
                try:
                    phone = store.xpath(".//p/a/text()")[0]
                except:
                    continue

                hours = "<MISSING>"
                try:
                    req = session.get(detail_url, headers=headers)
                    log.info(detail_url)
                    base = BeautifulSoup(req.text, "lxml")
                    hours = (
                        base.find(class_="schedule__body")
                        .ul.text.replace("\n", "; ")
                        .strip()
                    )
                except:
                    hours = "<INACCESSIBLE>"

                if hours[0] == ";":
                    hours = "".join(hours[1:]).strip()

                if street_address[-1] == ",":
                    street_address = "".join(street_address[:-1]).strip()
                yield SgRecord(
                    locator_domain="blomedry.com",
                    page_url=detail_url,
                    location_name=title,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipcode,
                    country_code=country,
                    store_number="<MISSING>",
                    phone=phone,
                    location_type="<MISSING>",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
