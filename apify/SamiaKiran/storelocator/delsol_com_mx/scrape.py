import json
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "delsol_com_tx"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

DOMAIN = "https://www.delsol.com.mx"
MISSING = SgRecord.MISSING


api_url = "https://www.delsol.com.mx/wcs/shop/AjaxProvinceSelectionDisplayView?catalogId=11501&storeId=1&langId=-5"
payload = "countryId=10001&requesttype=ajax"


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def get_data(loc):
    loc = json.loads(loc)
    location_name = strip_accents(loc["name"])
    street_address = strip_accents(loc["address"])
    log.info(location_name)
    city = strip_accents(loc["city"])
    state = strip_accents(loc["state"])

    raw_address = street_address + " " + city + " " + state
    pa = parse_address_intl(raw_address)

    street_address = pa.street_address_1
    street_address = street_address if street_address else MISSING

    zip_postal = pa.postcode
    zip_postal = zip_postal.strip() if zip_postal else MISSING
    zip_postal = zip_postal.replace("C.P.", "")
    latitude = loc["latitud"]
    longitude = loc["longitud"]
    return (
        location_name,
        street_address,
        city,
        state,
        zip_postal,
        latitude,
        longitude,
        raw_address,
    )


def fetch_data():
    if True:
        r = session.post(api_url, headers=headers, data=payload)
        soup = BeautifulSoup(r.text, "html.parser")
        state_list = soup.findAll("option")
        country_code = "MX"
        for state_url in state_list:
            log.info(f"Fetching states from {state_url.text}..............")
            url = "https://www.delsol.com.mx/wcs/shop/AjaxCitySelectionDisplayView?catalogId=11501&storeId=1&langId=-5"
            data = "provinceId=" + state_url["value"] + "&requesttype=ajax"
            r = session.post(url, headers=headers, data=data)
            soup = BeautifulSoup(r.text, "html.parser")
            city_list = soup.findAll("option")
            for city_url in city_list:
                url = "https://www.delsol.com.mx/wcs/shop/AjaxStoreLocatorResultsView?catalogId=11501&orderId=&storeId=1&langId=-5"
                data = (
                    "cityId="
                    + city_url["value"]
                    + "&fromPage=StoreLocator&geoCodeLatitude=&geoCodeLongitude=&errorMsgKey=&requesttype=ajax"
                )
                r = session.post(url, headers=headers, data=data)
                soup = BeautifulSoup(r.text, "html.parser")
                phone = soup.find("p", {"class", "phone"}).text
                loclist = soup.find("input")["value"]
                if "|" in loclist:
                    loclist = loclist.split("|")
                    for loc in loclist:
                        (
                            location_name,
                            street_address,
                            city,
                            state,
                            zip_postal,
                            latitude,
                            longitude,
                            raw_address,
                        ) = get_data(loc)
                        yield SgRecord(
                            locator_domain=DOMAIN,
                            page_url="https://www.delsol.com.mx/wcs/shop/es/delsol/sucursales",
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zip_postal,
                            country_code=country_code,
                            store_number=MISSING,
                            phone=phone,
                            location_type=MISSING,
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation="<INACCESIBLE>",
                            raw_address=raw_address,
                        )
                else:
                    (
                        location_name,
                        street_address,
                        city,
                        state,
                        zip_postal,
                        latitude,
                        longitude,
                        raw_address,
                    ) = get_data(loclist)
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url="https://www.delsol.com.mx/wcs/shop/es/delsol/sucursales",
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_postal,
                        country_code=country_code,
                        store_number=MISSING,
                        phone=phone,
                        location_type=MISSING,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation="<INACCESIBLE>",
                        raw_address=raw_address,
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
