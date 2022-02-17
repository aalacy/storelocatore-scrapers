# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.hsbc.com.mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://www.hsbc.com.mx"
    search_url = "https://www.hsbc.com.mx/contacto/directorio-de-sucursales/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath("//article[header]")

        for _, store in enumerate(stores, 1):

            page_url = (
                base + "".join(store.xpath(".//a/@href")).replace("//", "/") + "/"
            )
            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            locator_domain = website

            store_json = (
                store_res.text.split('<script type="application/ld+json">')[1]
                .split("</script>")[0]
                .strip()
            )
            store_info = json.loads(store_json)

            location_name = store_info["name"].strip()

            raw_address = "<MISSING>"
            street_address = store_info["address"]["streetAddress"].strip()
            city = store_info["address"]["addressLocality"].strip()
            state = "<MISSING>"
            temp_addr = store_sel.xpath(
                '//section[@class="M-CONTMAST-RW-RBWM"]//p[@class="A-PAR16R-RW-ALL"]'
            )
            if len(temp_addr) > 0:
                if "," in "".join(temp_addr[0].xpath("text()")).strip():
                    state = (
                        "".join(temp_addr[0].xpath("text()"))
                        .strip()
                        .split("\n")[1]
                        .strip()
                        .replace(",", "")
                        .strip()
                    )
            zip = store_info["address"]["postalCode"].strip()

            country_code = store_info["address"]["addressCountry"].strip()

            store_number = page_url.split("/")[-2].split("-")[0].strip()

            phone = "<MISSING>"
            if "contactPoint" in store_info:
                phone = store_info["contactPoint"][0]["telephone"]
            location_type = "<MISSING>"

            hour_list = []
            if "openingHoursSpecification" in store_info:
                hours = store_info["openingHoursSpecification"]
                for hour in hours:
                    day = hour["dayOfWeek"].split("/")[-1].strip()
                    hour_list.append(f'{day}: {hour["opens"]}-{hour["closes"]}')

            hours_of_operation = "; ".join(hour_list)
            for day in [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]:
                if day not in hours_of_operation:
                    hours_of_operation += f"; {day}: Closed"

            latitude, longitude = (
                store_info["geo"]["latitude"],
                store_info["geo"]["longitude"],
            )

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
                raw_address=raw_address,
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
