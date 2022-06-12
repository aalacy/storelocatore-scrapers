import csv
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from sglogging import sglog
from tenacity import retry, stop_after_attempt, wait_fixed


def get_countries():
    r = session.get(
        "https://co-opcreditunions.org/locator/?loctype=AS&t=2", headers=headers
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//select[@id='country']/option[@value!='']/@value")


def parse(js, page_url, sgw: SgWriter):
    try:
        for j in js:
            location_name = j.get("Name")
            street_address = j.get("Address")
            city = j.get("City")
            state = j.get("State") or ""
            if "," in state:
                state = state.replace(",", "").strip()
            postal = j.get("Zip") or ""
            if "-" in postal:
                postal = postal.split("-")[0].strip()
            if len(postal) == 4:
                postal = f"0{postal}"

            country = j.get("Country")
            phone = j.get("Phone") or ""
            if "/>" in phone:
                phone = phone.split("/>")[-1].strip()

            latitude = j.get("Latitude")
            longitude = j.get("Longitude")
            if not j.get("AcceptsDeposit"):
                location_type = "Shared Branch"
            else:
                location_type = "ATM"

            _tmp = []
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            for day in days:
                part = day[:3]
                start = j.get(f"Hours{part}Open")
                end = j.get(f"Hours{part}Close")
                if not start:
                    continue
                if "Closed" in start:
                    _tmp.append(f"{day}: Closed")
                else:
                    _tmp.append(f"{day}: {start} - {end}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country,
                location_type=location_type,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

    except Exception as e:
        logger.info(f"Error: {e}")


@retry(stop=stop_after_attempt(8), wait=wait_fixed(5))
def get_params(api):
    slug = api.split("?")[-1].replace("%22", "")
    page_url = f"https://co-opcreditunions.org/locator/search-results/?{slug}"

    logger.info(f"Crawling: {api}")

    r = session.get(api, headers=headers)
    js = csv.DictReader(r.iter_lines())
    return page_url, js


def fetch_data(sgw: SgWriter):
    international = get_countries()
    for i in international:
        api = f"https://co-opcreditunions.org/wp-content/themes/coop019901/inc/locator/locator-csv.php?loctype=AS&country={i}&Submit=Search%22"
        page_url, js = get_params(api)
        parse(js, page_url, sgw)

    search = DynamicZipSearch(
        country_codes=[
            SearchableCountries.USA,
        ],
        expected_search_radius_miles=1,
    )
    for _zip in search:
        api = f"https://co-opcreditunions.org/wp-content/themes/coop019901/inc/locator/locator-csv.php?loctype=AS&zip={_zip}&maxradius=10&country=&Submit=Search%22"
        page_url, js = get_params(api)
        parse(js, page_url, sgw)


if __name__ == "__main__":
    locator_domain = "https://www.co-opfs.org/Shared-Branches-ATMs"
    logger = sglog.SgLogSetup().get_logger(logger_name="co-opcreditunions.org")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_TYPE}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
