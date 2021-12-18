import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "https://caprabo.com/"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def get_hoo(loc):
    days = ["d", "j", "l", "m", "s", "v", "x"]
    engDays = [
        "Sunday",
        "Thursday",
        "Monday",
        "Tuesday",
        "Saturday",
        "Friday",
        "Wednesday",
    ]
    hoo = []
    keys = loc.keys()
    count = -1

    for day in days:
        count = count + 1
        dayKeys = []
        values = []

        for key in keys:
            if "hora_" + day + "_" in key:
                dayKeys.append(key)

        for dayKey in dayKeys:
            v = loc[dayKey]
            if v != "":
                values.append(v)
        values.sort()
        if len(values) == 0:
            continue
        if len(values) == 2:
            hoo.append(f"{engDays[count]}: {values[0]}: {values[1]}")
        if len(values) == 4:
            hoo.append(
                f"{engDays[count]}: {values[0]}: {values[1]}/ {values[2]}: {values[3]}"
            )

    if len(hoo) == 0:
        hoo = MISSING
    else:
        hoo = "; ".join(hoo)
    return hoo


def fetch_data():
    if True:
        url = "https://www.caprabo.com/system/modules/com.caprabo.mrmmccann.caprabocom.formatters/resources/js/localizador.js"
        r = session.get(url, headers=headers)
        loclist = json.loads(r.text.split("var json =")[1].split("}];")[0] + "}]")
        for loc in loclist:
            location_name = MISSING
            longitude = loc["longitud"].replace(",", ".")
            latitude = loc["latitud"].replace(",", ".")
            phone = loc["telefono"]
            street_address = strip_accents(loc["direccion"])
            city = strip_accents(loc["municipio"])
            state = strip_accents(loc["provincia"])
            zip_postal = loc["cp"]
            country_code = "SPAIN"
            hours_of_operation = get_hoo(loc)

            raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
                MISSING, ""
            )
            raw_address = " ".join(raw_address.split())
            raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
            if raw_address[len(raw_address) - 1] == ",":
                raw_address = raw_address[:-1]

            yield SgRecord(
                locator_domain=website,
                page_url="https://www.caprabo.com/ca/home/localizador-de-supermercados/",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
