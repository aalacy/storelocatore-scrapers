from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "synovus_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://synovus.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.synovus.com/locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    log.info("Fetching the Key for the API...")
    key = soup.select_one("script[src*=key]")["src"].split("key=")[1]
    state_list = ["Alabama", "Florida", "Georgia", "South Carolina", "Tennessee"]
    for temp_state in state_list:
        api_url = (
            "https://www.mapquestapi.com/search/v2/radius?origin="
            + temp_state
            + "&radius=1000&distanceUnit=dm&hostedData=mqap.36969_Synovus&ambiguities=ignore&key="
            + key
            + "&callback=window.MapManager.processSearchResults"
        )
        r = session.get(api_url, headers=headers)
        loclist = r.text.split("fields")[1:]
        for loc in loclist:
            location = '"fields' + loc
            location = location.rstrip(',"')
            location_type = location.split('"LocType":"', 1)[1].split('"')[0]
            page_url = location.split('"page_url":"', 1)[1].split('"')[0]
            if not page_url:
                page_url = url
            log.info(page_url)
            location_name = location.split('"Name":"', 1)[1].split('"')[0]
            latlng = location.split('"latLng":{', 1)[1].split("}")[0]
            longitude = latlng.split('"lng":', 1)[1].split(",")[0]
            latitude = latlng.split('"lat":', 1)[1]
            phone = location.split('"Phone":"', 1)[1].split('"')[0]
            if not phone:
                phone = MISSING
            street_address = location.split('"address":"', 1)[1].split('"')[0]
            city = location.split('"city":"', 1)[1].split('"')[0]
            state = location.split('"state":"', 1)[1].split('"')[0]
            zip_postal = location.split('"postal":"', 1)[1].split('"')[0]
            country_code = "US"
            Monday = location.split('"Monday":"', 1)[1].split('"')[0]
            Mon = ""
            if Monday == "":
                Mon = "Monday: " + "Closed"
            else:
                Mon = "Monday: " + Monday
            Tuesday = location.split('"Tuesday":"', 1)[1].split('"')[0]
            Tues = ""
            if Tuesday == "":
                Tues = "Tuesday: " + "Closed"
            else:
                Tues = "Tuesday: " + Tuesday
            Wednesday = location.split('"Wednesday":"', 1)[1].split('"')[0]
            Wed = ""
            if Wednesday == "":
                Wed = "Wednesday: " + "Closed"
            else:
                Wed = "Wednesday: " + Wednesday
            Thursday = location.split('"Thursday":"', 1)[1].split('"')[0]
            Thurs = ""
            if Thursday == "":
                Thurs = "Thursday: " + "Closed"
            else:
                Thurs = "Thursday: " + Thursday
            friday = location.split('"Friday":"', 1)[1].split('"')[0]
            fri = ""
            if friday == "":
                fri = "friday: " + "Closed"
            else:
                fri = "friday: " + friday
            saturday = location.split('"Saturday":"', 1)[1].split('"')[0]
            sat = ""
            if saturday == "":
                sat = "saturday: " + "Closed"
            else:
                sat = "saturday: " + saturday
            sunday = location.split('"Sunday":"', 1)[1].split('"')[0]
            sun = ""
            if sunday == "":
                sun = "Sunday: " + "Closed"
            else:
                sun = "Sunday: " + sunday
            Hours = (
                Mon
                + ", "
                + Tues
                + ", "
                + Wed
                + ", "
                + Thurs
                + ", "
                + fri
                + ", "
                + sat
                + ", "
                + sun
            )
            if (
                Hours
                == "Monday: , Tuesday: , Wednesday: , Thursday: , Friday: , Saturday: , Sunday: "
            ):
                Hours = MISSING
            Hours = Hours.rstrip()
            Hours = Hours.lstrip()
            if (
                Hours
                == "Monday: Closed, Tuesday: Closed, Wednesday: Closed, Thursday: Closed, friday: Closed, saturday: Closed, Sunday: Closed"
            ):
                Hours = "Closed"
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
                phone=phone.strip(),
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=Hours,
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
