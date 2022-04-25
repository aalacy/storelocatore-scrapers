from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgselenium import SgSelenium
from sgscrape.sgpostal import parse_address_intl
import ssl
import time

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "hokben.co.id"
LOCATION_URL = "https://www.hokben.co.id/outlet"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

CITIES = [
    "Banda Aceh",
    "Sabang",
    "Denpasar",
    "Pangkalpinang",
    "Cilegon",
    "Serang",
    "Tangerang Selatan",
    "Tangerang",
    "Bengkulu",
    "Yogyakarta",
    "Gorontalo",
    "Jakarta",
    "Jakarta Barat",
    "Cianjur",
    "Jakarta Pusat",
    "Jakarta Selatan",
    "Jakarta Timur",
    "Jakarta Utara",
    "Sungai Penuh",
    "Jambi",
    "Bandung",
    "Bekasi",
    "Bogor",
    "Pajajaran",
    "Botani",
    "Cimahi",
    "Cirebon",
    "Depok",
    "Sukabumi",
    "Tasikmalaya",
    "Banjar",
    "Magelang",
    "Pekalongan",
    "Salatiga",
    "Semarang",
    "Surakarta",
    "Tegal",
    "Batu",
    "Blitar",
    "Kediri",
    "Madiun",
    "Malang",
    "Mojokerto",
    "Pasuruan",
    "Probolinggo",
    "Surabaya",
    "Pontianak",
    "Singkawang",
    "Banjarbaru",
    "Banjarmasin",
    "Palangkaraya",
    "Balikpapan",
    "Bontang",
    "Samarinda",
    "Tarakan",
    "Batam",
    "Tanjungpinang",
    "Bandar Lampung",
    "Metro",
    "Ternate",
    "Tidore Kepulauan",
    "Ambon",
    "Tual",
    "Bima",
    "Mataram",
    "Kupang",
    "Sorong",
    "Jayapura",
    "Dumai",
    "Pekanbaru",
    "Makassar",
    "Palopo",
    "Parepare",
    "Palu",
    "Baubau",
    "Kendari",
    "Bitung",
    "Kotamobagu",
    "Manado",
    "Tomohon",
    "Bukittinggi",
    "Padang",
    "Padang Panjang",
    "Pariaman",
    "Payakumbuh",
    "Sawahlunto",
    "Solok",
    "Lubuklinggau",
    "Pagar Alam",
    "Palembang",
    "Prabumulih",
    "Sekayu",
    "Gunungsitoli",
    "Medan",
    "Padang Sidempuan",
    "Pematangsiantar",
    "Sibolga",
    "Tanjungbalai",
    "Tebing Tinggi",
]


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
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


def search_location(driver, city, num=0):
    num += 1
    input = driver.find_element_by_id("findAddress")
    input.clear()
    input.send_keys(city)
    try:
        driver.find_element_by_xpath("/html/body/div[5]/div[1]").click()
        driver.implicitly_wait(5)
    except:
        try:
            driver.find_element_by_xpath("/html/body/div[6]/div[1]").click()
            driver.implicitly_wait(5)
        except:
            if num <= 3:
                log.info(f"Search failed for {city}. retry num {num}")
                return search_location(driver, city, num)
            else:
                driver.refresh()
                driver.implicitly_wait(10)
                return search_location(driver, city)
    time.sleep(2)
    return driver


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    driver.implicitly_wait(10)
    for city in CITIES:
        driver = search_location(driver, city)
        soup = bs(driver.page_source, "lxml")
        contents = soup.find("div", id="list-store").find_all(
            "div", {"class": "col-12 col-md-4 mb-3"}
        )
        for row in contents:
            location_name = " ".join(row.find("h5").text.strip().split())
            raw_address = (
                row.find("p", {"class": "card-text small my-auto"})
                .get_text(strip=True, separator=",")
                .replace("Alamat :,", "")
                .replace("Kota", "")
                .strip()
            )
            street_address, _, state, zip_postal = getAddress(raw_address)
            street_address = " ".join(street_address.replace(city, "").split())
            if "Pajajaran" in city:
                city = "Bogor"
                street_address = street_address.replace("bogor", "").strip()
            phone = MISSING
            country_code = "ID"
            hours_of_operation = (
                row.find("p", {"class": "card-text small my-2"})
                .get_text(strip=True, separator=" ")
                .replace("Jam Buka :", "")
            )
            store_number = MISSING
            location_type = MISSING
            latitude = MISSING
            longitude = MISSING
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
                raw_address=raw_address,
            )
    driver.quit()


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
