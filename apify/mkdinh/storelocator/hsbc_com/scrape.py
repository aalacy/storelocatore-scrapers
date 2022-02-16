# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "hsbc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_urls = [
        "https://www.hsbc.com.ar/mapa/,   Argentina",
        "https://www.hsbc.bm/branch-finder/,  Bermuda",
        "https://www.hsbc.ca/branch-locator/, Canada",
        "https://www.hsbc.com.mx/contacto/sucursales/,    Mexico",
        "https://www.us.hsbc.com/branch-locator/, United States",
        "https://www.hsbc.com.au/branch-finder/,  Australia",
        "https://www.hsbc.com.cn/en-cn/branch-finder/,    China",
        "https://www.hsbc.com.hk/branch-finder/,  Hong Kong",
        "https://www.hsbc.co.in/branch-finder/,   India",
        "https://www.hsbc.com.mo/branch-finder/,  Macau",
        "https://www.hsbc.com.my/branch-finder/,  Malaysia",
        "https://www.hsbc.co.mu/branch-finder/,   Mauritius",
        "https://www.hsbc.com.ph/branch-finder/,  Philippines",
        "https://www.hsbc.com.sg/branch-finder/,  Singapore",
        "https://www.hsbc.lk/branch-finder/,  Sri Lanka",
        "https://www.hsbc.com.tw/en-tw/branch-finder/,    Taiwan",
        "https://www.hsbc.am/en-am/branch-finder/,    Armenia",
        "https://www.hsbc.gr/en-gr/branch-finder/,    Greece",
        "https://www.hsbc.com.mt/branch-finder/,  Malta",
        "https://www.hsbc.co.uk/branch-finder/,   UK",
        "https://www.hsbc.com.bh/branch-finder/,  Bahrain",
        "https://www.hsbc.com.eg/branch-finder/,  Egypt",
        "https://www.hsbc.co.om/branch-finder/,   Oman",
        "https://www.hsbc.com.qa/branch-finder/,  Qatar",
        "https://www.hsbc.ae/branch-finder/,  UAE",
    ]

    for url_country in search_urls:
        search_url = url_country.split(",")[0].strip()
        domain = (
            search_url.rsplit(".", 1)[0]
            + "."
            + search_url.rsplit(".", 1)[1].split("/")[0].strip()
        )
        log.info(search_url)
        home_req = session.get(search_url, headers=headers)
        home_sel = lxml.html.fromstring(home_req.text)
        data_files = eval(
            "".join(
                home_sel.xpath(
                    '//div[@class="branchLocator"]/@data-dpws-tool-datafiles'
                )
            ).strip()
        )
        for key in data_files.keys():
            url = data_files[key]
            stores_req = session.get(
                domain + url.replace(".cdata", ".udata"),
                headers=headers,
            )
            stores = json.loads(stores_req.text)[key]

            for store in stores:
                page_url = "<MISSING>"
                locator_domain = website
                location_name = store["name"]
                street_address = ""
                if "street" in store["address"]:
                    street_address = (
                        store["address"]["street"]
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "-")
                        .strip()
                        .replace("---", "-")
                        .strip()
                    )
                city = store["address"].get("townOrCity", "<MISSING>")
                state = store["address"].get("stateRegionCounty", "<MISSING>")
                zip = store["address"].get("postcode", "<MISSING>")
                country_code = url_country.split(",")[1].strip()
                phone = ""
                if "phoneNumber" in store:
                    phone = store["phoneNumber"][list(store["phoneNumber"].keys())[0]]

                store_number = "<MISSING>"
                location_type = store["Type"]
                page_url = "<MISSING>"

                hours_list = []
                if "openingTimes" in store:
                    hours = store["openingTimes"]
                    for day in hours.keys():
                        if "open" in hours[day] and "close" in hours[day]:
                            time = hours[day]["open"] + "-" + hours[day]["close"]
                            if "N/A" not in time:
                                hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()
                latitude = store["coordinates"]["lat"]
                longitude = store["coordinates"]["lng"]

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.COUNTRY_CODE,
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
