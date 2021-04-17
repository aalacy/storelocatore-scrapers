from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter


session = SgRequests()
website = "iwc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    page_result = 0
    current_offset = 0
    isFinish = False
    while isFinish is False:
        r = session.get(
            "https://stores.iwc.com/search?country=US&offset=" + str(current_offset),
            headers=headers,
        )
        json_data = r.json()
        page_result = len(json_data["response"]["entities"])
        current_offset += page_result
        for location in json_data["response"]["entities"]:
            street_address = (
                str(location["profile"]["address"]["line1"])
                + " "
                + str(location["profile"]["address"]["line2"])
                + " "
                + str(location["profile"]["address"]["line3"])
            )
            street_address = street_address.replace(" None", "")
            location_name = location["profile"]["name"].replace("&", "and")
            log.info(location_name)
            try:
                page_url = location["profile"]["c_pagesURL"].replace('"', "")
            except:
                page_url = "<MISSING>"
            state = location["profile"]["address"]["region"]
            city = location["profile"]["address"]["city"]
            zip_postal = location["profile"]["address"]["postalCode"]
            country_code = location["profile"]["address"]["countryCode"]
            try:
                phone = location["profile"]["mainPhone"]["display"]
            except:
                phone = "<MISSING>"
            try:
                latitude = location["profile"]["displayCoordinate"]["lat"]
                longitude = location["profile"]["displayCoordinate"]["long"]
            except:
                latitude = location["profile"]["yextDisplayCoordinate"]["lat"]
                longitude = location["profile"]["yextDisplayCoordinate"]["long"]

            hours_of_operation = ""
            if "hours" in location["profile"]:
                for days_hours in location["profile"]["hours"]["normalHours"]:
                    if days_hours["isClosed"] is False:
                        hours_of_operation += (
                            days_hours["day"]
                            + " "
                            + str(days_hours["intervals"][0]["start"] / 100).replace(
                                ".", ":"
                            )
                            + "0 - "
                            + str(days_hours["intervals"][0]["end"] / 100).replace(
                                ".", ":"
                            )
                            + "0"
                        )
                    else:
                        hours_of_operation += days_hours["day"] + " Closed"

                    hours_of_operation += " "
            hours_of_operation = hours_of_operation.capitalize()
            yield SgRecord(
                locator_domain="https://www.iwc.com",
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number="<MISSING>",
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )
        if page_result == 0:
            isFinish = True


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
