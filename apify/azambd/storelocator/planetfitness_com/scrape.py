import time

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgrequests import SgRequests
from sglogging import sglog
import tenacity

session = SgRequests()

MISSING = SgRecord.MISSING

DOMAIN = "planetfitness.com"

website = "https://www.planetfitness.com/gyms/"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


headersAPI = {
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Origin": "https://www.planetfitness.com",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.planetfitness.com/",
    "Accept-Language": "en-US,en;q=0.9",
}

headersPFX = {
    "authority": "www.planetfitness.com",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.planetfitness.com/gyms/",
    "accept-language": "en-US,en;q=0.9",
    "cookie": '_gid=GA1.2.1406649780.1620725732; _gcl_au=1.1.1440677928.1620725733; _hjid=591cf9d7-7b4b-41d6-8e05-29ae3c6680fe; _pin_unauth=dWlkPU5EVTVOVEl3TkRNdFpXSTJOeTAwTWpabExXSXlPVGd0WkRkak9HRTBOREUyT1dZeA; _fbp=fb.1.1620725734232.1032952514; _scid=c8888212-5552-4849-9fa5-748e3f979362; _sctr=1|1620669600000; _gaexp=GAX1.2.Ty5K6yklRYWLQ_t4Kl5DjQ.18831.1; pfx_join_experience=new; _hjIncludedInSessionSample=0; _hjTLDTest=1; _hjAbsoluteSessionInProgress=0; _csrf-pf-website=Sv6L7YGfA8YqdfY1rKPtHFaV; istio-fingerprint="04a024dfb10b43d8"; locale=en_US; AWSALB=uqUmo3SmTjC/+8kemQnhi+OVSTRIwEXXL+PTDC77hB9WpdoUOqG/THS/iOHqIs/ZeSm4aBnkgUe8gXUzuYlP3Sn5ya9xNotNa+KNV4TJcU79F8CrjkVf+/TDeh0R; AWSALBCORS=uqUmo3SmTjC/+8kemQnhi+OVSTRIwEXXL+PTDC77hB9WpdoUOqG/THS/iOHqIs/ZeSm4aBnkgUe8gXUzuYlP3Sn5ya9xNotNa+KNV4TJcU79F8CrjkVf+/TDeh0R; _ga_NPH7H94TXH=GS1.1.1620793619.4.1.1620794764.59; _uetsid=3c3928e0b23c11eb97004ffe6b0e7735; _uetvid=3c3943f0b23c11eb938ab9bc57e75351; _ga=GA1.2.970905619.1620725732; _gat_UA-27725796-5=1',
}


def reqFirstAPI(url):
    return session.get(url, headers=headersAPI).json()


@tenacity.retry(wait=tenacity.wait_fixed(5))
def reqDetailPageAPI(url):
    return session.get(url, headers=headersPFX).json()


def fetchData():
    apiUrl = "https://cde-assets-planetfitness.s3.amazonaws.com/locations.json"
    dpid = reqFirstAPI(apiUrl)
    d = dpid["clubs"]
    log.info(f"Total Locations: {len(d)}")
    for i in d:
        pfxid = i["id"]
        pfxurl = "https://www.planetfitness.com/gyms/pfx/api/clubs/" + str(pfxid)
        log.info(f"PFXURL: {pfxurl}")

        jd = reqDetailPageAPI(pfxurl)

        # Page url
        page_url = website + jd["slug"] or MISSING

        # Name
        location_name = jd["name"] or MISSING

        # Store
        store_number = jd["pfClubId"] or MISSING

        # Phone
        phone = jd["telephone"] or MISSING

        # Latitude
        latitude = jd["location"]["latitude"] or MISSING

        # Longitude
        longitude = jd["location"]["longitude"] or MISSING

        # Street
        street_address = jd["location"]["address"]["line1"] or MISSING

        # City
        city = jd["location"]["address"]["city"] or MISSING

        # State
        state = jd["location"]["address"]["stateCode"] or MISSING

        # Zip Code
        zip_postal = jd["location"]["address"]["postalCode"] or MISSING

        # Country Code
        country_code = jd["location"]["address"]["countryCode"] or MISSING

        # HOO
        hours = jd["hours"]["description"] or MISSING
        hours_of_operation = (
            hours.replace("\r\n\r\n", ", ").replace("\r\n", ", ").replace("\n", ", ")
        )

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            phone=phone,
            location_type="Gym",
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()
    result = fetchData()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total rows added = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
