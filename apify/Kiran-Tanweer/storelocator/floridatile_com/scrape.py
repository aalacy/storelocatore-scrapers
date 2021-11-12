from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup


session = SgRequests()
website = "floridatile_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}
headers2 = {
    'authority': 'in.getclicky.com',
    'method': 'POST',
    'path': '/in.php?site_id=101187675&type=ping&jsuid=2412129655&hmset&mime=js&x=0.46474500551401476',
    'scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'content-length': '100000',
    'content-type': 'text/plain;charset=UTF-8',
    'cookie': 'cluid=2412129655',
    'origin': 'https://www.floridatile.com',
    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    "Referer": "https://www.floridatile.com/store-locator/",
    "X-CSRFToken": "haPUjfbIdmWdMLaagkZfBOvQK0J3EkOEhmgqpGqpgr5MVbim6w2xQFxZDbAGikOR"
    }

payload = "{operationName:searchLocations,variables:{latitude:41.8780025,longitude:-93.097702,locationTypes:[Dealer,Distributor,Florida Tile],miles:500,first:100},query:query searchLocations(`$before: String, `$after: String, `$first: Int, `$last: Int, `$latitude: Float!, `$longitude: Float!, `$miles: Int!, `$locationTypes: [String]!) {\\n  searchLocations(before: `$before, after: `$after, first: `$first, last: `$last, latitude: `$latitude, longitude: `$longitude, miles: `$miles, locationTypes: `$locationTypes) {\\n    edges {\\n      node {\\n        id\\n        name\\n        dealerId\\n        address\\n        city\\n        state\\n        zipCode\\n        country\\n        phone\\n        point\\n        fullAddress\\n        website\\n        locationType\\n        distance\\n        __typename\\n      }\\n      __typename\\n    }\\n    pageInfo {\\n      hasNextPage\\n      hasPreviousPage\\n      startCursor\\n      endCursor\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n}"

DOMAIN = "https://www.floridatile.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = 'https://www.floridatile.com/graphql'
        stores_req = session.post(search_url, headers=headers2, data=payload)
##            soup = BeautifulSoup(stores_req.text, "html.parser")
        print(stores_req)
            

##
##            yield SgRecord(
##                locator_domain=DOMAIN,
##                page_url=loc_link,
##                location_name=title,
##                street_address=street.strip(),
##                city=city.strip(),
##                state=state.strip(),
##                zip_postal=pcode,
##                country_code="US",
##                store_number=storeid,
##                phone=phone,
##                location_type=MISSING,
##                latitude=lat,
##                longitude=lng,
##                hours_of_operation=hours.strip(),
##            )
##
##
##def scrape():
##    log.info("Started")
##    count = 0
##    deduper = SgRecordDeduper(
##        SgRecordID(
##            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
##        )
##    )
##    with SgWriter(deduper) as writer:
##        results = fetch_data()
##        for rec in results:
##            writer.write_row(rec)
##            count = count + 1
##    log.info(f"No of records being processed: {count}")
##    log.info("Finished")
##
##
##if __name__ == "__main__":
##    scrape()

fetch_data()
