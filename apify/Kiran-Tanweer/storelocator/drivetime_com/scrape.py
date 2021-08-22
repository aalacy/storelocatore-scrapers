import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter


session = SgRequests()
website = "drivetime_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Length": "319",
    "Content-Type": "application/json",
    "Host": "online-search.drivetime.com",
    "Origin": "https://www.drivetime.com",
    "Referer": "https://www.drivetime.com/",
    "sec-ch-ua": 'Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "x-ms-azs-return-searchid": "true",
}


DOMAIN = "https://www.drivetime.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://online-search.drivetime.com/search/indexes/dealershipsindex/docs/search"
        payload = '{"search":"*","select":"*","top":99999,"skip":0,"count":"true"}'
        loclist = session.post(url, headers=headers, data=payload).json()["value"]
        for loc in loclist:
            location_name = loc["DealershipName"]
            store_number = loc["DealershipNumber"]
            page_url = (
                "https://www.drivetime.com/pelham/al/car-dealers/"
                + location_name.lower()
                + "/"
                + str(store_number)
            )
            page_url = page_url.replace(" ", "-")
            log.info(page_url)
            phone = loc["PhoneNumber"]
            temp = json.loads(str(loc["Schedule"]).replace("]", "").replace("[", ""))
            hours_of_operation = (
                "Monday: "
                + temp["MondayOpen"]
                + "-"
                + temp["MondayClosed"]
                + " Tuesday: "
                + temp["TuesdayOpen"]
                + "-"
                + temp["TuesdayClosed"]
                + " Wednesday: "
                + temp["WednesdayOpen"]
                + "-"
                + temp["WednesdayClosed"]
                + " Thursday: "
                + temp["ThursdayOpen"]
                + "-"
                + temp["ThursdayClosed"]
                + " Friday: "
                + temp["FridayOpen"]
                + "-"
                + temp["FridayClosed"]
                + " Saturday: "
                + temp["SaturdayOpen"]
                + "-"
                + temp["SaturdayClosed"]
            )
            hours_of_operation = hours_of_operation + " Sunday: Closed"
            street_address = loc["AddressLine1"]
            city = loc["City"]
            zip_postal = loc["Zip5"]
            country_code = "US"
            state = loc["StateAbbreviation"]
            coords = loc["GeoPoint"]["coordinates"]
            latitude = coords[1]
            longitude = coords[0]
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
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
