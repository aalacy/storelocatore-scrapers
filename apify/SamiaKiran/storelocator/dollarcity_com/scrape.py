import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests(verify_ssl=False)
website = "amerisbank_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
}
DOMAIN = "https://www.amerisbank.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def parse_time(time, day):
    return (
        day
        + " "
        + time.split("[{'StartTime': '")[1].split("'")[0]
        + "-"
        + time.split("'EndTime': '")[1].split("'")[0]
    )


def fetch_data():
    state_list = {
        "https://dollarcity.com/ubicaciones/locations/GetDataByCoordinates?longitude=-77.0622315&latitude=-12.077182&distance=10000&units=kilometers&amenities=&paymentMethods=&filter=PE",
        "https://dollarcity.com/ubicaciones/locations/GetDataByCoordinates?longitude=-90.53139&latitude=14.62278&distance=10000&units=kilometers&amenities=&paymentMethods=&filter=GT",
        "https://dollarcity.com/ubicaciones/locations/GetDataByCoordinates?longitude=-89.05668800000001&latitude=13.442909&distance=10000&units=kilometers&amenities=&paymentMethods=&filter=SV",
        "https://dollarcity.com/ubicaciones/locations/GetDataByCoordinates?longitude=-74.054854&latitude=4.667418&distance=10000&units=kilometers&amenities=&paymentMethods=&filter=CO",
    }
    for state_url in state_list:
        loclist = session.post(state_url, headers=headers).json()["StoreLocations"]
        for loc in loclist:
            hours = loc["ExtraData"]["HoursOfOpStruct"]
            su = parse_time(str(hours["Su"]["Ranges"]), "Sun")
            mo = parse_time(str(hours["Mo"]["Ranges"]), "Mon")
            tu = parse_time(str(hours["Tu"]["Ranges"]), "Tue")
            we = parse_time(str(hours["We"]["Ranges"]), "Wed")
            th = parse_time(str(hours["Th"]["Ranges"]), "Thu")
            fr = parse_time(str(hours["Fr"]["Ranges"]), "Fri")
            sa = parse_time(str(hours["Sa"]["Ranges"]), "Sat")
            hours_of_operation = (
                mo + " " + tu + " " + we + " " + th + " " + fr + " " + sa + " " + su
            )
            location_name = strip_accents(loc["ExtraData"]["Name"]["LongName"])
            log.info(location_name)
            store_number = loc["LocationNumber"]
            temp = loc["Location"]
            coords = temp["coordinates"]
            longitude = coords[0]
            latitude = coords[1]
            address = loc["ExtraData"]["Address"]
            phone = loc["ExtraData"]["Phone"]
            try:
                street_address = address["AddressNonStruct_Line1"]

            except:
                street_address = address["AddressNonStruct_Line2"]

            street_address = strip_accents(street_address)
            if "," in street_address:
                street_address = street_address.split(",")[0]
            city = strip_accents(address["Locality"])
            try:
                state = strip_accents(address["RegionName"])
            except:
                state = MISSING
            zip_postal = address["PostalCode"]
            if zip_postal is None:
                zip_postal = MISSING
            country_code = address["CountryCode"]
            if "SV" in state_url:
                country = "elsalvador"
            elif "GT" in state_url:
                country = "guatemala"
            elif "CO" in state_url:
                country = "colombia"
            elif "PE" in state_url:
                country = "peru"
            try:
                append_state = address["Region"].lower().replace(" ", "-")
            except:
                append_state = ""
            append_city = city.lower().replace(" ", "-").replace(".", "-").strip("-")
            append_location_name = location_name.lower().replace(" ", "-")
            page_url = (
                "https://dollarcity.com/ubicaciones/es-gt/locations/"
                + country
                + "/"
                + append_state
                + "/"
                + append_city
                + "/"
                + append_location_name
            ).replace("//", "/")
            page_url = strip_accents(page_url)
            log.info(page_url)
            raw_address = (
                address["AddressNonStruct_Line1"]
                + ", "
                + city
                + ", "
                + state
                + ", "
                + zip_postal
            )
            raw_address = strip_accents(raw_address.replace(MISSING, ""))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
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
