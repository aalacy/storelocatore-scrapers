import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "bellacinos_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://bellacinos.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    daylist = {
        "1": "Monday",
        "2": "Tuesday",
        "3": "Wednesday",
        "4": "Thursday",
        "5": "Friday",
        "6": "Saturday",
        "7": "Sunday",
    }
    url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=BAVYISWKYNNQTIXK&center=31.8039734986,-98.8223185136653&coordinates=10.74167474861858,-141.02202554491512,37.493303137349145,-106.62261148241522&multi_account=false&page=1&pageSize=60"
    r = session.get(url, headers=headers)
    loclist = json.loads(r.text)
    link_list = "https://locations.bellacinos.com/sitemap.xml"
    r = session.get(link_list, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    link_list = soup.findAll("loc")
    for loc in loclist:
        phone = loc["store_info"]["phone"]
        location_name = loc["store_info"]["name"]
        temp = loc["store_info"]["address"]
        temp = temp.replace(" ", "-")
        for link in link_list:
            link = str(link)
            if temp in link:
                page_url = (
                    link.replace("<loc>", "")
                    .replace("</loc>", "")
                    .replace(
                        "https://locations.bellacinosgrinders.com/",
                        "https://locations.bellacinos.com/",
                    )
                )
                break
        try:
            street_address = (
                loc["store_info"]["address"]
                + " "
                + loc["store_info"]["address_extended"]
            )
        except:
            street_address = loc["store_info"]["address"]
        log.info(page_url)
        city = loc["store_info"]["locality"]
        state = loc["store_info"]["region"]
        zip_postal = loc["store_info"]["postcode"]
        country_code = loc["store_info"]["country"]
        store_number = loc["store_info"]["corporate_id"]
        latitude = loc["store_info"]["latitude"]
        longitude = loc["store_info"]["longitude"]
        hour_list = loc["store_info"]["store_hours"]
        if not hour_list:
            hours_of_operation = MISSING
        else:
            hour_list = hour_list.split(";")
            hour_list = hour_list[:-1]
            if len(hour_list) < 7:
                if "1," not in hour_list[0]:
                    hour_list.insert(0, "1,Closed,")
                elif "7," not in hour_list[5]:
                    hour_list.append("7,Closed,")
            hours_of_operation = ""
            for hour in hour_list:
                hour = hour.split(",")
                day = daylist[hour[0]]
                open_time = hour[1]
                close_time = hour[2]
                hours_of_operation = (
                    hours_of_operation + day + " " + open_time + "-" + close_time + " "
                )
        hours_of_operation = hours_of_operation.replace("Closed-", "Closed")
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=url,
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
            hours_of_operation=hours_of_operation.strip(),
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
