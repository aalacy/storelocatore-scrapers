from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_usa

DOMAIN = "homehardware.ca"
BASE_URL = "https://www.homehardware.ca/"
LOCATION_URL = "https://www.homehardware.ca/en/store-locator"
API_URL = "https://www.homehardware.ca/api/content/documentlists/store-templates-hh-boh@HomeH/views/default/documents?filter=properties.displayOnline%20eq%20true%20and%20properties.storeType%20in[%27Home%20Hardware%27,%27Home%20Building%20Centre%27,%27Home%20Hardware%20Building%20Centre%27]&pageSize=1100"
HEADERS = {
    "Accept": "application/json",
    "Content-type": "application/json",
    "cookie": "_mzvr=A_DnVvEW10W_IPL03B4AeQ; hhLanguage=en; _mzvs=nn; _mzvt=sRWZAt7ZoECT0XXBbzb3Xg; sb-sf-at-prod-s=pt=&at=MdlFwKGDYJ5HUmhtqfZijQpXXMJE1PX3OKSF4/frTq/yens/zgvYd+MBerjMG0s/oHojEFwBQxechFQ54+Sjpl00pT24ci9wUJt1ULb8GsDK0hQF6n1JvDnFeNMRei77e99/BvDsGGorMSqBK9U8Zs5VdvBaR+vO7b14G4LrtZV//hNSj0Mzew7kn85XY3HJ8Xi7mRA0A25+r92V2TkxB1cRpHndCgyYYELfHzcFIeDq+t4FhlnWWFzj35y2RKnjSrauROkol6GH3LOegevClNmTyoBHkW/yC7xmsZjYwOY0lbXsP5UzCyqMqqoa5igL/aFB2bOxtgS46VwV9dkdpg==&dt=2019-09-02T17:20:12.7247459Z; sb-sf-at-prod=pt=&at=MdlFwKGDYJ5HUmhtqfZijQpXXMJE1PX3OKSF4/frTq/yens/zgvYd+MBerjMG0s/oHojEFwBQxechFQ54+Sjpl00pT24ci9wUJt1ULb8GsDK0hQF6n1JvDnFeNMRei77e99/BvDsGGorMSqBK9U8Zs5VdvBaR+vO7b14G4LrtZV//hNSj0Mzew7kn85XY3HJ8Xi7mRA0A25+r92V2TkxB1cRpHndCgyYYELfHzcFIeDq+t4FhlnWWFzj35y2RKnjSrauROkol6GH3LOegevClNmTyoBHkW/yC7xmsZjYwOY0lbXsP5UzCyqMqqoa5igL/aFB2bOxtgS46VwV9dkdpg==; mozucartcount=%7B%22be9da37b74d642e69f0d75040708a04b%22%3A0%7D; _mzPc=eyJjb3JyZWxhdGlvbklkIjoiMmUyZDBkYzNkNGJhNGI1YjhkM2I4YzlmOTllYmJhM2YiLCJpcEFkZHJlc3MiOiIxMDMuOS4xOTEuMTg5IiwiaXNEZWJ1Z01vZGUiOmZhbHNlLCJpc0NyYXdsZXIiOmZhbHNlLCJpc01vYmlsZSI6ZmFsc2UsImlzVGFibGV0IjpmYWxzZSwiaXNEZXNrdG9wIjp0cnVlLCJ2aXNpdCI6eyJ2aXNpdElkIjoic1JXWkF0N1pvRUNUMFhYQmJ6YjNYZyIsInZpc2l0b3JJZCI6IkFfRG5WdkVXMTBXX0lQTDAzQjRBZVEiLCJpc1RyYWNrZWQiOmZhbHNlLCJpc1VzZXJUcmFja2VkIjpmYWxzZX0sInVzZXIiOnsiaXNBdXRoZW50aWNhdGVkIjpmYWxzZSwidXNlcklkIjoiYmU5ZGEzN2I3NGQ2NDJlNjlmMGQ3NTA0MDcwOGEwNGIiLCJmaXJzdE5hbWUiOiIiLCJsYXN0TmFtZSI6IiIsImVtYWlsIjoiIiwiaXNBbm9ueW1vdXMiOnRydWUsImJlaGF2aW9ycyI6WzEwMTQsMjIyXX0sInVzZXJQcm9maWxlIjp7InVzZXJJZCI6ImJlOWRhMzdiNzRkNjQyZTY5ZjBkNzUwNDA3MDhhMDRiIiwiZmlyc3ROYW1lIjoiIiwibGFzdE5hbWUiOiIiLCJlbWFpbEFkZHJlc3MiOiIiLCJ1c2VyTmFtZSI6IiJ9LCJpc0VkaXRNb2RlIjpmYWxzZSwiaXNBZG1pbk1vZGUiOmZhbHNlLCJub3ciOiIyMDE5LTA5LTAyVDE3OjQxOjIzLjU0NjkxOTRaIiwiY3Jhd2xlckluZm8iOnsiaXNDcmF3bGVyIjpmYWxzZSwiY2Fub25pY2FsVXJsIjoiL3N0b3JlLWxvY2F0b3IifSwiY3VycmVuY3lSYXRlSW5mbyI6e319",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data["items"]:
        location_name = row["properties"]["storeName"]
        street_address = (
            (row["properties"]["address1"] + " " + row["properties"]["address2"])
            .replace("N/A", "")
            .replace("\n", "")
            .strip()
        )
        city = row["properties"]["city"]
        state = row["properties"]["province"][0]
        zip_postal = row["properties"]["postalCode"]
        country_code = "CA"
        store_number = row["name"]
        phone = (
            row["properties"]["phone"]
            .replace(" (204) 878-2583", "")
            .replace(", (C) (226) 883-0750", "")
        ).strip()
        location_type = row["properties"]["storeType"][0]
        latitude = row["properties"]["latitude"]
        longitude = row["properties"]["longitude"]
        hoo = ""
        hours = ""
        days = ["Sunday", "Monday", "Tuesday", "Thursday", "Friday", "Saturday"]
        for day in days:
            hours += row["properties"][day.lower() + "Hours"] + " "
            hoo += day + ": " + row["properties"][day.lower() + "Hours"] + ","
        hours_of_operation = hoo.rstrip(",").strip()
        if len(hours.strip()) == 0:
            hours_of_operation = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
            raw_address=f"{street_address}, {city}, {state}, {zip_postal}",
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
