import html
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "mycdi_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

DOMAIN = "https://mycdi.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://rayusradiology.com/wp-admin/admin-ajax.php"
        payload = {"action": "get_procedures_list"}
        loclist = session.post(url, headers=headers, data=payload).json()
        for loc in loclist:
            location_name = loc["post_title"]
            store_number = loc["post_id"]
            page_url = loc["post_link"]
            log.info(page_url)
            phone = loc["telephone_number"]
            hours_of_operation = loc["office_hours"]
            hours_of_operation = (
                hours_of_operation.replace("\n", " ")
                .replace("(MRI and X-Ray)", "")
                .replace("(every other week)", "")
                .replace("Call for availability and dates.", "")
            )
            if "Weekend" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Weekend")[0]
            elif "Hours" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Hours")[0]
            elif "Evening" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Evening")[0]
            elif "(MRI" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("(MRI")[0]
            elif "Evening" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Evening")[0]
            hours_of_operation = html.unescape(hours_of_operation)
            location_name = html.unescape(location_name)
            try:
                street_address = (
                    loc["street_address"] + " " + loc["street_address_line_2"]
                )
            except:
                street_address = loc["street_address"]
            city = loc["city"]
            zip_postal = loc["zipcode"]
            country_code = "US"
            state = loc["state"]
            latitude = loc["lat"]
            longitude = loc["lng"]
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
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )


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
