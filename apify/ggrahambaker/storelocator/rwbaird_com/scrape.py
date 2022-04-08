from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import json

DOMAIN = "rwbaird.com"
API_URL = "http://www.locatebaird.com/locator/api/InternalSearch"
HEADERS = {
    "Host": "www.locatebaird.com",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "http://www.locatebaird.com",
    "DNT": "1",
    "Connection": "keep-alive",
    "Cookie": 'settings={"AuthenticatedMethods":[]}; PresenterX.T=130381A5B562ADBD9A9BBDA23C23137B107AADD1145876BA2DE0780BBE53A6C7BD749573A16906814522D916848C40CC21B880B8FCCE9875EC6D6705E72EECFE3571AD34F90B29AB8A96162F7B65C8E44CA40E1DBB3C433ADCA4EB633DD4B2CE8E29DF21FFF11176FEFA1084F892BD217C75B003BC978EC7814D212C275C4E8005A613CC6F06BAD3581CC9392962C64792C0E3D4AA584EB8DB21160E4EC0AD57F3A753EB6C143AC7B00EC5311440D4AD7FD728B6; presenter=30dfa3dbca46f1a40af76941f1219685c855415d4d072409eb3e572e00fb41afe6eba520',
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

COOKIES = {
    "presenter": "30dfa3dbca46f1a40af76941f1219685c855415d4d072409eb3e572e00fb41afe6eba520",
    "PresenterX.T": "130381A5B562ADBD9A9BBDA23C23137B107AADD1145876BA2DE0780BBE53A6C7BD749573A16906814522D916848C40CC21B880B8FCCE9875EC6D6705E72EECFE3571AD34F90B29AB8A96162F7B65C8E44CA40E1DBB3C433ADCA4EB633DD4B2CE8E29DF21FFF11176FEFA1084F892BD217C75B003BC978EC7814D212C275C4E8005A613CC6F06BAD3581CC9392962C64792C0E3D4AA584EB8DB21160E4EC0AD57F3A753EB6C143AC7B00EC5311440D4AD7FD728B6",
    "settings": '{"AuthenticatedMethods":[]}',
}

MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=100
    )
    for zip_code in search:
        url = "http://www.locatebaird.com/branch-results.htm?zipcode=" + str(zip_code)
        HEADERS["Referer"] = url
        PARAMS = {
            "Locator": "BAIRD",
            "City": "",
            "Region": "",
            "PostalCode": str(zip_code),
            "Country": "USA",
            "Company": " ",
            "ProfileTypes": "Branch",
            "DoFuzzyNameSearch": "0",
            "SearchRadius": "100",
        }
        r = session.post(
            API_URL,
            headers=HEADERS,
            data=json.dumps(PARAMS),
            cookies=COOKIES,
        )
        log.info(f"Searching locations for => {zip_code}")
        res_json = json.loads(r.content)["Results"]
        if not res_json:
            continue
        log.info(f"Found {len(res_json)} locations on => {zip_code}")
        for loc in res_json:
            location_name = loc["Company"]
            store_number = loc["ProfileId"]
            street_address = loc["Address1"] + " " + loc["Address2"]
            street_address = street_address.strip()
            city = loc["City"]
            state = loc["Region"]
            zip_postal = loc["PostalCode"]
            country_code = "US"
            latitude = loc["GeoLat"]
            longitude = loc["GeoLon"]
            more_loc = loc["XmlData"]["parameters"]
            if more_loc["SiteIsLive"] == "0":
                continue
            try:
                page_url = more_loc["Url"]
            except:
                page_url = "https://www.rwbaird.com/who-we-are/locations/"
            if "LocalNumber" not in more_loc:
                try:
                    phone = more_loc["TollFreeNumber"]
                except:
                    phone = MISSING
            else:
                phone = more_loc["LocalNumber"]
            location_type = MISSING
            hours_of_operation = MISSING
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
