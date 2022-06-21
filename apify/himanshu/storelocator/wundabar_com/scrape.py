# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("wundabar_com")
session = SgRequests()


def fetch_data():
    base_url = "https://www.wundabar.com/studios"
    r = session.get(base_url)
    main_soup = BeautifulSoup(r.text, "lxml")
    data1 = main_soup.find_all("a", {"class": "image-slide-anchor content-fill"})

    for index, i in enumerate(data1):

        k = []

        while len(k) == 0:
            page_url = "https://www.wundabar.com" + i["href"]
            r = session.get(page_url)
            soup = BeautifulSoup(r.text, "lxml")
            k = soup.find_all("div", {"class": "sqs-block html-block sqs-block-html"})

        for j in k:
            info = list(j.stripped_strings)
            state = ""
            zipcode = ""
            if "CONTACT" in info or len(info) == 1:
                pass
            else:
                logger.info(info)
                if "new client" in info[0]:
                    info = info[1:]

                street_address = info[0]
                city = info[1].split(",")[0]
                location_name = city
                state_zip = info[1].split(",")[1].split()
                if len(state_zip) == 3:
                    state = state_zip[0] + " " + state_zip[1]
                    zipcode = state_zip[2]
                else:
                    state = state_zip[0]
                    zipcode = state_zip[1]

                phone = info[2]

                yield SgRecord(
                    locator_domain="wundabar.com",
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipcode,
                    country_code="US",
                    store_number="<MISSING>",
                    phone=phone,
                    location_type="<MISSING>",
                    latitude="<MISSING>",
                    longitude="<MISSING>",
                    hours_of_operation="<MISSING>",
                )


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
