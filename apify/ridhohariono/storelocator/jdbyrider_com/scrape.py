from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "jdbyrider.com"
API_ENDPOINT = "https://www.byrider.com/wp-admin/admin-ajax.php?action=get_locations_details&locIds=AL106%2CFL161%2CFL163%2CAR102%2CAR101%2CAR103%2CAR104%2CAZ103%2CAZ109%2CCO107%2CCT103%2CFL139%2CFL154%2CFL162%2CIA104%2CIA109%2CIA110%2CIA111%2CMO109%2CMO113%2CID101%2CIL105%2CIL116%2CIL115%2CIL121%2CIL125%2CIL131%2CIL117%2CIL119%2CIL122%2CILC40%2CINC39%2CIN115%2CINC02%2CINC03%2CINC05%2CINC07%2CINC10%2CKYC20%2COH112%2COH127%2COH134%2COH143%2COH144%2COH145%2COH150%2COHC09%2COHC11%2COHC12%2COHC13%2COHC18%2COHC19%2CPA103%2CPA104%2CPA112%2CPA113%2CPA114%2CTN107%2CIN116%2CIN116A%2CIN116B%2CIN116C%2CIN116D%2CIN116H%2CMO110%2CKY104%2CMI115%2CIN125%2CMA102%2CMA108%2CMD102%2CIN124%2CMI105%2CMI108%2CMI109%2CMI113%2CMO112%2CMS104%2CMS105%2CNC112%2CNH101%2CNY107%2CWV104%2CWV105%2CWV106%2CWV107%2CWV109%2COH130%2COH140%2COH142%2COH148%2COH152%2COH132%2CPA110%2CFL164%2CPA108%2CPA111%2CPA115%2CPA116%2CPA117%2CMA104%2CRI101%2CSC105%2CSC114%2CSC115%2CTX109%2CTX115%2CTX116%2CTX112%2CTX114%2CTX122%2CTX118%2CVA102%2CWI102%2CWI104%2CWI107%2CWI110%2CWI112%2CWI111%2CWI115%2CWI114%2CKY106%2CWV108%2CCO108%2CIL132%2CID102%2CAL112%2CWI116%2CMD106%2CTNC41%2CWI117%2CBDNC01%2CBDNC02%2COHC06%2CILC42%2CTX129%2CAR106%2CMI116%2CLA110%2CAR107%2CGA108%2CROTX01%2CMO114%2CIN127%2CKY107"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_ENDPOINT, headers=HEADERS).json()
    for key, val in data.items():
        if not val or val["location_is_closed"]:
            continue
        page_url = val["dealershipPageUri"]
        location_name = val["_BusName"]
        street_address = (val["_BusAddr1"] + " " + val["_BusAddr2"]).strip()
        city = val["_BusCity"]
        state = val["_BusStateCd"]
        zip_postal = val["_BusZipCd"]
        phone = val["_SalesPhoneNumber"]
        country_code = "US"
        store_number = val["_LocId"]
        hours_of_operation = ""
        for hoo in val["_SalesHours"]:
            if hoo["isClosed"]:
                hour = "Closed"
            else:
                hour = hoo["openTime"] + " - " + hoo["closeTime"]
            hours_of_operation += hoo["dayOfWeek"] + ": " + hour + ","
        hours_of_operation = hours_of_operation.rstrip(",")
        latitude = val["latitude"]
        longitude = val["longitude"]
        location_type = val["_SrvType"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
