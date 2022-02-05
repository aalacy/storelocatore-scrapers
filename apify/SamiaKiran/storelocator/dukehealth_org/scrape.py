import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "dukehealth_org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


payload = json.dumps(
    {
        "endpoint": "/locationSearch",
        "params": {
            "q": "",
            "fq": [],
            "fl": "its_nid,tm_X3b_en_title,ss_url,reference_coordinates,sm_location_location_type_name,sm_treatment_term_name,tm_X3b_en_organization,tm_X3b_en_address_line1,ss_field_phone_number_url,tm_X3b_en_address_line2,tm_X3b_en_postal_code,ss_field_clockwisemd_location_id,ss_field_header_image_url,tm_X3b_en_field_appoint_phone,ss_field_preview_image_path,tm_X3b_en_locality,tm_X3b_en_administrative_area_code,patient_age_group,tm_X3b_en_field_office_phone,ss_field_epic_provider_id,bs_field_has_open_scheduling,ss_field_google_map_url,sm_field_hospital_phone",
            "start": 0,
            "rows": 9999,
            "sort": "sm_aggregated_field_title asc",
            "facet.field": [
                "{u0021ex=ttn}sm_treatment_term_name",
                "{u0021ex=ltn}sm_location_location_type_name",
                "{u0021ex=pag}patient_age_group",
            ],
        },
    }
)

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Content-Type": "application/json",
    "Origin": "https://www.dukehealth.org",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.dukehealth.org/locations",
    "Accept-Language": "en-US,en;q=0.9",
}

DOMAIN = "https://www.dukehealth.org/"
MISSING = SgRecord.MISSING


def fetch_data():
    url_list = []
    if True:
        day_list = {
            1: "Mon",
            2: "Tue",
            3: "Wed",
            4: "Thu",
            5: "Fri",
            6: "Sat",
            7: "Sun",
        }
        url = "https://www.dukehealth.org/solr/select?_format=json"
        loclist = session.post(url, headers=headers, data=payload).json()["response"][
            "docs"
        ]
        for loc in loclist:
            page_url = "https://www.dukehealth.org" + loc["ss_url"]
            if page_url in url_list:
                continue
            url_list.append(page_url)
            log.info(page_url)
            try:
                street_address = (
                    loc["tm_X3b_en_address_line1"][0]
                    + " "
                    + loc["tm_X3b_en_address_line2"][0]
                )
            except:
                street_address = loc["tm_X3b_en_address_line1"][0]
            try:
                latitude, longitude = loc["reference_coordinates"].split(",")
            except:
                latitude = MISSING
                longitude = MISSING
            city = loc["tm_X3b_en_locality"][0]
            state = loc["tm_X3b_en_administrative_area_code"][0]
            zip_postal = loc["tm_X3b_en_postal_code"][0]

            try:
                location_type = loc["sm_location_location_type_name"][0]
            except:
                location_type = MISSING
            store_number = str(loc["its_nid"])
            location_name = loc["tm_X3b_en_title"][0].split("-")[0]
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                hour_list = soup.find(
                    "div", {"class": "clinic-hours-desktop text-center"}
                ).findAll("td")
                count = 1
                hours_of_operation = ""
                for hour in hour_list:
                    day = day_list[count]
                    count = count + 1
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + day
                        + " "
                        + hour.get_text(separator="|", strip=True).replace("|", " ")
                    )
            except:
                hours_of_operation = MISSING
            try:
                phone = loc["tm_X3b_en_field_office_phone"][0]
            except:
                try:
                    phone = loc["sm_field_hospital_phone"][0]
                except:
                    try:
                        phone = soup.findAll(
                            "strong", {"class": "contact-number"}
                        ).text[1]
                    except:
                        phone = soup.select_one("a[href*=tel]").text
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
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
