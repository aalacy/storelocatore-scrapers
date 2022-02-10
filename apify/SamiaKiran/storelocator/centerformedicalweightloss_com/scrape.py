import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "centerformedicalweightloss_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

DOMAIN = "https://centerformedicalweightloss.com/"
MISSING = SgRecord.MISSING


headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "Origin": "https://centerformedicalweightloss.com",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://centerformedicalweightloss.com/find_a_center.aspx",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_data():
    url = "https://centerformedicalweightloss.com/find_a_center.aspx"
    zips = static_zipcode_list(radius=50, country_code=SearchableCountries.USA)
    for zip_code in zips:
        payload = (
            "__VIEWSTATE=%2FwEPDwUENTM4MQ8WAh4TVmFsaWRhdGVSZXF1ZXN0TW9kZQIBFgJmD2QWAmYPZBYCZg9kFgJmD2QWBAIDD2QWBgIEDxYCHgdWaXNpYmxlaGQCBg8WAh8BaGQCCA8WAh8BaGQCBw9kFgICAQ9kFgICAhBkZBYCAhMPZBYEAgEPPCsACwBkAgMPPCsACwBkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYBBU9jdGwwMCRjdGwwMCRjdGwwMCRDb250ZW50UGxhY2VIb2xkZXJEZWZhdWx0JENvbnRlbnRCb2R5JEZpbmRfQV9DZW50ZXIkYnRuU3VibWl0RteXrK6bfB4%2BsHDVgavEcKjF2F%2BzPWkAKcy%2F4YF5cec%3D&ctl00%24ctl00%24ctl00%24ContentPlaceHolderDefault%24ContentBody%24Find_A_Center%24zipCodeInputAdv=&ctl00%24ctl00%24ctl00%24ContentPlaceHolderDefault%24ContentBody%24Find_A_Center%24nameInput=&ctl00%24ctl00%24ctl00%24ContentPlaceHolderDefault%24ContentBody%24Find_A_Center%24HtmlHiddenField=ZipSearch&ctl00%24ctl00%24ctl00%24ContentPlaceHolderDefault%24ContentBody%24Find_A_Center%24milesInput=50&ctl00%24ctl00%24ctl00%24ContentPlaceHolderDefault%24ContentBody%24Find_A_Center%24zipCodeInput="
            + zip_code
            + "&ctl00%24ctl00%24ctl00%24ContentPlaceHolderDefault%24ContentBody%24Find_A_Center%24btnSubmit.x=72&ctl00%24ctl00%24ctl00%24ContentPlaceHolderDefault%24ContentBody%24Find_A_Center%24btnSubmit.y=11&defaultMiles=50&__VIEWSTATEGENERATOR=CA0B0334&__EVENTTARGET=&__EVENTARGUMENT="
        )
        r = session.post(url, data=payload, headers=headers)
        loclist = r.text.split("centersData=")[1].split(";</script></div>", 1)[0]
        loclist = json.loads(loclist)
        for loc in loclist:
            location_name = loc["name"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            page_url = (
                "https://centerformedicalweightloss.com/doctors?url=" + loc["urlslug"]
            )
            log.info(page_url)
            phone = loc["tollfree"]
            street_address = loc["address1"] + " " + loc["address2"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"].split("-")[0]
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
