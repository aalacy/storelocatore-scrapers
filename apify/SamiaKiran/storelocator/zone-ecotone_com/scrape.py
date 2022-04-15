from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "zone-ecotone_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
  'authority': 'sheets.googleapis.com',
  'accept': '*/*',
  'accept-language': 'en-US,en;q=0.9',
  'origin': 'https://zone-ecotone.com',
  'referer': 'https://zone-ecotone.com/',
  'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'cross-site',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
 }

DOMAIN = "https://zone-ecotone.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://zone-ecotone.com/en/pages/magasins"
        r = session.get(url)
        log.info("Fetching API Token...")
        api_key = r.text.split('data-api-key="')[1].split('"')[0]
        doc_id = r.text.split('"doc_id":"')[1].split('"')[0]
        api_url = "https://sheets.googleapis.com/v4/spreadsheets/"+doc_id+"/values/Feuille%201?key="+api_key
        loclist = session.get(api_url, headers=headers).json()['values'][1:]
        for loc in loclist:
            location_name = loc[0]
            log.info(location_name)
            loc = loc[3:]
            street_address = loc[0]
            city = loc[1].replace("QC",'')
            state = "QC"
            phone = loc[2]
            latitude = loc[-2]
            longitude = loc[-1]
            zip_postal = loc[-3]
            country_code = "CA"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
