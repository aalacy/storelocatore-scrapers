import json
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "louispion_fr"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.louispion.fr/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://boutiques.louispion.fr"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("a", {"class": "em-seo-indexes__link"})
        for link in linklist:
            url = "https://boutiques.louispion.fr" + link["href"]
            r = session.get(url, headers=headers)
            schema = r.text.split(
                '<script id="__NEXT_DATA__" type="application/json">'
            )[1].split("</script>", 1)[0]
            schema = schema.replace("\n", "")
            loclist = json.loads(schema)["props"]["pageProps"]["dualFrameData"][
                "poisListData"
            ]
            for loc in loclist:
                store_number = loc["code"]
                address = loc["address"]
                latitude = loc["position"]["Latitude"]
                longitude = loc["position"]["Longitude"]
                hour_list = loc["schedules"]["Defaultweekschedule"]
                hours_of_operation = ""
                for hour in hour_list:
                    day = hour["name"]
                    try:
                        value = hour["values"]["OpeningRanges"][0]
                    except:
                        continue
                    begin = value["BeginTime"]
                    end = value["EndTime"]
                    time = (
                        str(begin["Hour"])
                        + ":"
                        + str(begin["Minute"])
                        + "-"
                        + str(end["Hour"])
                        + ":"
                        + str(end["Minute"])
                    )
                    hours_of_operation = hours_of_operation + " " + day + " " + time
                loc = loc["metadata"]
                phone = loc["contacts"]["Phone"]
                try:
                    street_address = (
                        address["AddressLine1"] + " " + address["AddressLine"]
                    )
                except:
                    street_address = address["AddressLine1"]
                street_address = strip_accents(street_address)
                city = strip_accents(address["City"])
                state = MISSING
                zip_postal = address["PostalCode"]
                country_code = address["Country"]
                temp = loc["details"]
                location_name = temp["Name"]
                page_url = (
                    "https://boutiques.louispion.fr/fr/france-FR/"
                    + store_number
                    + "/"
                    + location_name.lower().replace(" ", "-")
                    + "/details"
                )
                log.info(page_url)
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
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
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
