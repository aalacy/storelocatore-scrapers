import re
import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "amerisbank_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.amerisbank.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    bank_locations_url = "https://banks.amerisbank.com/"
    r = session.get(bank_locations_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    for bank_state_link in soup.find_all(
        "a", {"linktrack": re.compile("State index page")}
    ):
        r = session.get(bank_state_link["href"], headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for bank_city_link in soup.find_all(
            "a", {"dta-linktrack": re.compile("City index page -")}
        ):
            r = session.get(bank_city_link["href"], headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            for branch_link in soup.find_all("a", {"linktrack": "Landing page"}):
                page_url = branch_link["href"]
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                log.info(page_url)
                data = (
                    soup.find_all("script", {"type": "application/ld+json"})[-1]
                ).text
                data1 = data.replace(
                    "//if applied, use the tmpl_var to retrieve the database value", ""
                )

                json_data = json.loads(data1)

                location_name = soup.find("div", {"id": "branchName"}).text.strip()
                street_address = json_data["address"]["streetAddress"]
                city = json_data["address"]["addressLocality"]
                state = json_data["address"]["addressRegion"]
                zip_postal = json_data["address"]["postalCode"]
                country_code = json_data["address"]["addressCountry"]
                store_number = json_data["@id"]
                if store_number.isdigit():
                    store_number = store_number
                else:
                    store_number = MISSING
                if json_data["telephone"]:
                    phone = json_data["telephone"]
                else:
                    phone = "866.616.6020"
                location_type = json_data["@type"]
                latitude = json_data["geo"]["latitude"]
                longitude = json_data["geo"]["longitude"]
                try:
                    hours = " ".join(
                        list(
                            soup.find(
                                "div", {"class": "flexRight hideATMNo"}
                            ).stripped_strings
                        )
                    )

                except:
                    try:
                        hours = " ".join(
                            list(
                                soup.find(
                                    "div", {"class": "flexRight hideATM"}
                                ).stripped_strings
                            )
                        )
                    except:
                        hours = " ".join(
                            list(
                                soup.find(
                                    "div", {"class": "flexRight"}
                                ).stripped_strings
                            )
                        )
                if "n/a" in hours or "N/A" in hours:
                    hours = "<MISSING>"
                if "24 Hour Access" in hours:
                    location_type = "ATM's"
                hours = (
                    hours.replace(
                        "Drive-Thru Hours Monday: Drive-Thru Service Not Available Tuesday: Drive-Thru Service Not Available Wednesday: Drive-Thru Service Not Available Thursday: Drive-Thru Service Not Available Friday: Drive-Thru Service Not Available Saturday: Drive-Thru Service Not Available Sunday: Drive-Thru Service Not Available ",
                        "",
                    )
                    .replace("HOURS ", "")
                    .replace("By Appointment Only", "")
                    .replace(" Drive-Thru Hours", ", Drive-Thru Hours")
                    .replace("Branch Lobby Hours ", "")
                )
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
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours.strip(),
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
