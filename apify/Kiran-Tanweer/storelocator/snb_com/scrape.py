import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup


session = SgRequests()
website = "snb_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://snb.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        p = session.get(
            "https://public.websteronline.com/location/1550-flatbush-ave-brooklyn-ny",
            headers=headers,
        )
        bs = BeautifulSoup(p.text, "html.parser")

        all_json = bs.find("script", {"type": "application/json"})
        all_json = str(all_json)
        all_json = all_json.replace(
            '<script data-drupal-selector="drupal-settings-json" type="application/json">',
            "",
        )
        all_json = all_json.replace("</script>", "")
        all_json = json.loads(all_json)
        for loc in all_json["wbLocationFinder"]["locations"]:
            name = loc["attributes"]["title"]
            store_id = loc["id"]
            url = "https://public.websteronline.com/" + loc["url"]
            lat = loc["attributes"]["geolocation"]["lat"]
            lng = loc["attributes"]["geolocation"]["lng"]
            street = (
                loc["attributes"]["address"]["street_1"]
                + " "
                + loc["attributes"]["address"]["street_2"]
            )
            city = loc["attributes"]["address"]["city"]
            state = loc["attributes"]["address"]["state"]
            pcode = loc["attributes"]["address"]["zip"]
            country = loc["attributes"]["address"]["country"]
            phone = loc["attributes"]["phone"]

            is_branch = loc["attributes"]["branch"]
            is_atm = loc["attributes"]["atm"]
            is_itm = loc["attributes"]["itm"]

            if is_branch is True:
                store_type = "branch"
            if is_atm is True:
                store_type = "ATM"
            if is_itm is True:
                store_type = "ITM"

            if phone is None:
                phone = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"

            hours = loc["attributes"]["open_hours"]
            if hours is not None:
                day1 = loc["attributes"]["open_hours"]["sunday"]
                if day1 is not None:
                    day1 = (
                        loc["attributes"]["open_hours"]["sunday"][0]["start"][
                            "formatted"
                        ]
                        + "-"
                        + loc["attributes"]["open_hours"]["sunday"][0]["end"][
                            "formatted"
                        ]
                    )
                if day1 is None:
                    day1 = "Closed"
                day2 = (
                    "monday"
                    + ":"
                    + loc["attributes"]["open_hours"]["monday"][0]["start"]["formatted"]
                    + "-"
                    + loc["attributes"]["open_hours"]["monday"][0]["end"]["formatted"]
                )
                day3 = (
                    "tuesday"
                    + ":"
                    + loc["attributes"]["open_hours"]["tuesday"][0]["start"][
                        "formatted"
                    ]
                    + "-"
                    + loc["attributes"]["open_hours"]["tuesday"][0]["end"]["formatted"]
                )
                day4 = (
                    "wednesday"
                    + ":"
                    + loc["attributes"]["open_hours"]["wednesday"][0]["start"][
                        "formatted"
                    ]
                    + "-"
                    + loc["attributes"]["open_hours"]["wednesday"][0]["end"][
                        "formatted"
                    ]
                )
                day5 = (
                    "thursday"
                    + ":"
                    + loc["attributes"]["open_hours"]["thursday"][0]["start"][
                        "formatted"
                    ]
                    + "-"
                    + loc["attributes"]["open_hours"]["thursday"][0]["end"]["formatted"]
                )
                day6 = (
                    "friday"
                    + ":"
                    + loc["attributes"]["open_hours"]["friday"][0]["start"]["formatted"]
                    + "-"
                    + loc["attributes"]["open_hours"]["friday"][0]["end"]["formatted"]
                )
                day7 = loc["attributes"]["open_hours"]["saturday"]
                if day7 is not None:
                    day7 = (
                        loc["attributes"]["open_hours"]["saturday"][0]["start"][
                            "formatted"
                        ]
                        + "-"
                        + loc["attributes"]["open_hours"]["saturday"][0]["end"][
                            "formatted"
                        ]
                    )
                if day7 is None:
                    day7 = "Closed"

                hours = (
                    "sunday: "
                    + day1
                    + " "
                    + day2
                    + " "
                    + day3
                    + " "
                    + day4
                    + " "
                    + day5
                    + " "
                    + day6
                    + "saturday: "
                    + day7
                )

            else:
                hours = MISSING

            if lat == "0" and lng == "0":
                lat = MISSING
                lng = MISSING

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=name,
                street_address=street.strip(),
                city=city.replace(",", "").strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=country,
                store_number=store_id,
                phone=phone.strip(),
                location_type=store_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
