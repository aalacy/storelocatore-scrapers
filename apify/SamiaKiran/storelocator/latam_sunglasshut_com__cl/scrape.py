import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "latam_sunglasshut_com__cl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://latam.sunglasshut.com/cl/"
MISSING = SgRecord.MISSING

headers_2 = {
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
}

API_ENDPOINT = "https://latam.sunglasshut.com/cl/js_cargarSelect2.php"


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        templist = []
        url = "https://latam.sunglasshut.com/cl/tienda.php"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        state_list = soup.find("select", {"id": "state"}).findAll("option")[1:]
        log.info("Fetching data from States.....")
        for state_value in state_list:
            payload = "edo_tienda=" + str(state_value["value"]) + "&query=P"
            city_list = session.post(
                API_ENDPOINT, headers=headers_2, data=payload
            ).json()["contenido"]
            if len(city_list) == 1:
                city_value = str(city_list[0]).split("|")[0]
                api_payload_data = (
                    "edo_tienda="
                    + str(state_value["value"])
                    + "&id_prov="
                    + city_value
                    + "&query=D"
                )
                templist.append(api_payload_data)
            else:
                for city in city_list:
                    city_value = str(city).split("|")[0]
                    api_payload_data = (
                        "edo_tienda="
                        + str(state_value["value"])
                        + "&id_prov="
                        + city_value
                        + "&query=D"
                    )
                    templist.append(api_payload_data)
            for temp in templist:
                payload = temp
                loclist = session.post(
                    API_ENDPOINT, headers=headers_2, data=payload
                ).json()["contenido"]
                for loc in loclist:
                    loc = loc.split("|")
                    location_name = loc[0]
                    log.info(location_name)
                    raw_address = loc[1]
                    pa = parse_address_intl(raw_address)

                    street_address = pa.street_address_1
                    street_address = street_address if street_address else MISSING

                    city = pa.city
                    city = city.strip() if city else MISSING

                    state = pa.state
                    state = state.strip() if state else MISSING

                    zip_postal = pa.postcode
                    zip_postal = zip_postal.strip() if zip_postal else MISSING
                    latitude, longitude = (
                        str(loc[2]).split("l=")[1].split("&z")[0].split(",")
                    )
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=url,
                        location_name=location_name,
                        street_address=street_address.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=zip_postal.strip(),
                        country_code="CL",
                        store_number=MISSING,
                        phone=MISSING,
                        location_type=MISSING,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=MISSING,
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
