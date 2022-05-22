import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "csas_cz"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://www.csas.cz"
MISSING = SgRecord.MISSING


def strip_accents(text):
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    return str(text)


def fetch_data():
    if True:
        url = "https://www.csas.cz/cs/pobocky-a-bankomaty#/?type=BRANCH&flags=POBOCKY"
        r = session.get(url)
        log.info("Fetching the WEB_API_key....")
        WEB_API_key = r.text.split('<script defer src="')[1].split('"')[0]
        r = session.get(WEB_API_key)
        WEB_API_key = r.text.split('apiKey:"')[1].split('",')[0]
        headers = {
            "Connection": "keep-alive",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            "Accept": "application/json, text/plain, */*",
            "WEB-API-key": WEB_API_key,
            "Accept-Language": "cs",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
            "sec-ch-ua-platform": '"Windows"',
            "Origin": "https://www.csas.cz",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.csas.cz/",
        }
        api_url = "https://api.csas.cz/webapi/api/v3/places?country=CZ&detail=FULL&&radius=100000000&size=1000&sort=distance&types=BRANCH"
        loclist = session.get(api_url, headers=headers).json()["items"]
        for loc in loclist:
            location_name = strip_accents(loc["name"])
            try:
                phone = loc["phones"][0]
            except:
                phone = loc["manager"]["phones"][0]
            street_address = strip_accents(loc["address"])
            city = strip_accents(loc["city"])
            state = strip_accents(loc["region"])
            zip_postal = loc["postCode"]
            country_code = loc["country"]
            latitude = loc["location"]["lat"]
            longitude = loc["location"]["lng"]
            store_number = loc["id"]
            page_url = (
                "https://www.csas.cz/cs/pobocky-a-bankomaty#/"
                + str(store_number)
                + "/"
                + street_address.lower()
                .replace(".", "")
                .replace(" ", "_")
                .replace("/", "_")
                + "_"
                + city.lower().replace(" ", "_")
            )
            log.info(page_url)
            hour_list = loc["openingHoursWithOutages"]
            hours_of_operation = ""
            for hour in hour_list:
                weekday = hour["weekday"]
                time = hour["intervals"]
                time1 = time[0]["from"] + "-" + time[0]["to"]
                try:
                    time2 = time[1]["from"] + "-" + time[1]["to"]
                except:
                    time2 = ""
                hours_of_operation = (
                    hours_of_operation + " " + weekday + " " + time1 + ", " + time2
                )
            if "SATURDAY" not in hours_of_operation:
                hours_of_operation = hours_of_operation + " SATURDAY CLOSED"
            if "SUNDAY" not in hours_of_operation:
                hours_of_operation = hours_of_operation + " SUNDAY CLOSED"
            hours_of_operation = hours_of_operation.strip().strip(",")
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
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
