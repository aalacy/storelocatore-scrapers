# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "atlanticare.org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.atlanticare.org/find-a-location/?page=1&count=10000"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        json_text = (
            stores_req.text.split("var moduleInstanceData_IH_PublicDetailView")[-1]
            .strip()
            .split("=", 1)[1]
            .strip()
            .split("};")[0]
            .strip()
            + "}"
        )
        json_data = json.loads(json_text)
        stores = json.loads(json_data["SettingsData"].encode("utf-8"))["MapItems"]
        for store in stores:
            page_url = "https://www.atlanticare.org" + store["DirectUrl"]
            log.info(page_url)
            locator_domain = website
            location_name = store["Title"].split(",")[0].strip()
            address = store["LocationAddress"]
            street_address = ""
            city = ""
            state = ""
            zip = ""
            if address and ", ," not in address:
                street_address = "".join(address.split(",")[:-2]).strip()
                city = address.split(",")[-2].strip()
                state = address.split(",")[-1].strip().rsplit(" ", 1)[0].strip()
                zip = address.split(",")[-1].strip().rsplit(" ", 1)[1].strip()

                is_digit = True
                for z in zip:
                    if z.isalpha():
                        is_digit = False
                        break

                if is_digit is False:
                    state = state + " " + zip
                    zip = "<MISSING>"

                zip = (
                    zip.encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "")
                    .strip()
                )
            country_code = "<MISSING>"

            store_number = "<MISSING>"
            phone = store["LocationPhoneNum"]

            latitude = ""
            longitude = ""
            if "Latitude" in store:
                latitude = store["Latitude"]

            if "Longitude" in store:
                longitude = store["Longitude"]

            location_type = ""
            hours_of_operation = ""

            store_req = session.get(page_url, headers=headers)
            store_json_text = (
                store_req.text.split("var moduleInstanceData_IH_PublicDetailView")[-1]
                .strip()
                .split("=", 1)[1]
                .strip()
                .split("</script>")[0]
                .strip()
                .rsplit("};", 1)[0]
                .strip()
                + "}"
            )
            store_json_data = json.loads(store_json_text)
            store_json = json.loads(store_json_data["SettingsData"].encode("utf-8"))

            temp_fields = store_json["StaticPageZones"][0]["Value"]["FieldColumns"]
            loc_type_list = []
            for field in temp_fields:
                sub_fields = field["Fields"]
                for s in sub_fields:
                    if "Services" == s["FieldName"]:
                        FieldColumns = s["FieldColumns"]
                        for col in FieldColumns:
                            fields = col["Fields"]
                            for f in fields:
                                if "ServiceName" == f["FieldName"]:
                                    loc_type_list.append(f["Value"])

                    if "LocationHours" == s["FieldName"]:
                        hours_of_operation = ";".join(s["Values"]).strip()

            location_type = ";".join(loc_type_list).strip()

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
