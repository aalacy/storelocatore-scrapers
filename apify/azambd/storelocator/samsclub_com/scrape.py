from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "samsclub.com"
website = "https://www.samsclub.com"
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def requests_with_retry(url):
    return session.get(url, headers=headers).json()


def threeDays(h):
    days = ["saturdayHrs", "sundayHrs", "monToFriHrs"]
    hoo = []
    for day in days:
        startHrs = h[f"{day}"]["startHrs"]
        endHrs = h[f"{day}"]["endHrs"]
        hooday = day.replace("Hrs", "").replace("monToFri", "mon-fri")
        hoo.append(f"{hooday}:{startHrs}-{endHrs}")
    hours_of_operation = ";".join(hoo)

    return hours_of_operation


def sevenDays(h):
    days = [
        "saturdayHrs",
        "sundayHrs",
        "mondayHrs",
        "tuesdayHrs",
        "wednesdayHrs",
        "thursdayHrs",
        "fridayHrs",
    ]
    hoo = []
    for day in days:
        startHrs = h[f"{day}"]["startHrs"]
        endHrs = h[f"{day}"]["endHrs"]
        hooday = day.replace("Hrs", "")
        hoo.append(f"{hooday}:{startHrs}-{endHrs}")
    hours_of_operation = ";".join(hoo)

    return hours_of_operation


def fetchData():

    apiurl = "https://www.samsclub.com/api/node/vivaldi/v2/clubfinder/list?distance=10000&nbrOfStores=2000&singleLineAddr=NY"
    r = requests_with_retry(apiurl)

    for i in r:
        store_number = i["id"]
        location_name = i["name"]
        street_address = i["address"]["address1"]
        city = i["address"]["city"]
        state = i["address"]["state"]
        zip_postal = i["address"]["postalCode"]
        phone = i["phone"]
        country_code = i["address"]["country"]
        latitude = i["geoPoint"]["latitude"]
        longitude = i["geoPoint"]["longitude"]
        page_url = "https://www.samsclub.com/club/" + str(store_number)
        rawHrs = i["operationalHours"]

        if len(rawHrs) == 3:
            hours_of_operation = threeDays(rawHrs)
        else:
            hours_of_operation = sevenDays(rawHrs)

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            phone=phone,
            location_type="<MISSING>",
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Crawling Started")
    count = 0
    results = fetchData()
    with SgWriter() as writer:
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
