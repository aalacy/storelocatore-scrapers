from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "steward_org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.steward.org/"
MISSING = SgRecord.MISSING


url = "https://locations.steward.org/s/sfsites/aura?r=5&aura.ApexAction.execute=2"

headers = {
    "authority": "locations.steward.org",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Mobile Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "accept": "*/*",
    "origin": "https://locations.steward.org",
}


def fetch_data():
    if True:
        state_list = [
            "Arizona",
            "Arkansas",
            "Massachusetts",
            "New Hampshire",
            "Texas",
            "Florida",
            "Ohio",
            "Utah",
            "Louisiana",
            "Pennsylvania",
        ]
        for state_temp in state_list:
            log.info(f"Fetching Locations from {state_temp}")
            payload = (
                "message=%7B%22actions%22%3A%5B%7B%22id%22%3A%22160%3Ba%22%2C%22descriptor%22%3A%22aura%3A%2F%2FApexActionController%2FACTION%24execute%22%2C%22callingDescriptor%22%3A%22UNKNOWN%22%2C%22params%22%3A%7B%22namespace%22%3A%22%22%2C%22classname%22%3A%22MapboxController%22%2C%22method%22%3A%22getSettings%22%2C%22cacheable%22%3Afalse%2C%22isContinuation%22%3Afalse%7D%7D%2C%7B%22id%22%3A%22161%3Ba%22%2C%22descriptor%22%3A%22aura%3A%2F%2FApexActionController%2FACTION%24execute%22%2C%22callingDescriptor%22%3A%22UNKNOWN%22%2C%22params%22%3A%7B%22namespace%22%3A%22%22%2C%22classname%22%3A%22ProviderSearchController%22%2C%22method%22%3A%22getProviders%22%2C%22params%22%3A%7B%22queryParams%22%3A%7B%22searchTerm%22%3A%22null%22%2C%22location%22%3A%22"
                + state_temp
                + "%22%2C%22geolocation%22%3Anull%2C%22gender%22%3Anull%2C%22proximity%22%3Anull%2C%22bookable%22%3Anull%2C%22newPatients%22%3Anull%2C%22ageGroup%22%3Anull%2C%22networkAffiliation%22%3Anull%2C%22hospitalAffiliations%22%3Anull%2C%22languages%22%3Anull%2C%22filter%22%3A%22basic%22%7D%7D%2C%22cacheable%22%3Afalse%2C%22isContinuation%22%3Afalse%7D%7D%5D%7D&aura.context=%7B%22mode%22%3A%22PROD%22%2C%22fwuid%22%3A%22QbIGjbUweWP5tLmFUE_dTw%22%2C%22app%22%3A%22siteforce%3AcommunityApp%22%2C%22loaded%22%3A%7B%22APPLICATION%40markup%3A%2F%2Fsiteforce%3AcommunityApp%22%3A%22KbCmDBVbE10iCy1inwbbzA%22%7D%2C%22dn%22%3A%5B%5D%2C%22globals%22%3A%7B%7D%2C%22uad%22%3Afalse%7D&aura.pageURI=%2Fs%2Fprovider-search-results%3FsearchTerm%3Dnull%26location%3D"
                + state_temp
                + "%26filter%3Dbasic&aura.token=null"
            )
            linklist = session.post(url, headers=headers, data=payload).json()[
                "actions"
            ][1]["returnValue"]["returnValue"]
            for link in linklist:
                loclist = link["Contact"]["Affiliations__r"]
                for loc in loclist:
                    page_url = (
                        "https://locations.steward.org/s/affiliation/" + loc["Id"]
                    )
                    log.info(page_url)
                    loc = loc["Account__r"]
                    location_name = loc["Name"]
                    address = loc["ShippingAddress"]
                    street_address = address["street"].replace("\n", " ")
                    city = address["city"]
                    state = address["state"]
                    zip_postal = address["postalCode"]
                    country_code = "US"
                    try:
                        latitude = loc["ShippingLatitude"]
                    except:
                        latitude = MISSING
                    try:
                        longitude = loc["ShippingLongitude"]
                    except:
                        longitude = MISSING
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=zip_postal.strip(),
                        country_code=country_code,
                        store_number=MISSING,
                        phone="<INACCESSIBLE>",
                        location_type=MISSING,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation="<INACCESSIBLE>",
                    )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
