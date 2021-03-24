from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "petsuitesofamerica_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    url = "https://liveapi.yext.com/v2/accounts/me/entities?filter=%7B%20%22meta.folderId%22%3A%7B%22%24in%22%3A[249017]%7D%7D&limit=50&api_key=2bc9758495549d8bd15fe1c10fdcd617&v=20161012"
    loclist = session.get(url, headers=headers).json()["response"]["entities"]
    for loc in loclist:
        try:
            page_url = loc["c_baseURL"]
        except:
            page_url = "<MISSING>"
        try:
            location_name = loc["facebookName"]
        except:
            location_name = loc["name"]
        street_address = loc["address"]["line1"]
        city = loc["address"]["city"]
        state = loc["address"]["region"]
        zip_postal = loc["address"]["postalCode"]
        country_code = loc["address"]["countryCode"]
        latitude = loc["cityCoordinate"]["latitude"]
        longitude = loc["cityCoordinate"]["longitude"]
        log.info(page_url)
        try:
            phone = loc["c_websitePhone"]
        except:
            phone = loc["mainPhone"]
        try:
            store_number = loc["c_websiteID"]
        except:
            if "<MISSING>" not in page_url:
                r = session.get(page_url, headers=headers)
                store_number = r.text.split("'websiteId': '")[1].split("'", 1)[0]
            else:
                store_number = "<MISSING>"
        mon = loc["hours"]["monday"]["openIntervals"][0]
        mon_s = mon["start"]
        mon_e = mon["end"]
        tue = loc["hours"]["tuesday"]["openIntervals"][0]
        tue_s = tue["start"]
        tue_e = tue["end"]
        wed = loc["hours"]["wednesday"]["openIntervals"][0]
        wed_s = wed["start"]
        wed_e = wed["end"]
        thu = loc["hours"]["thursday"]["openIntervals"][0]
        thu_s = thu["start"]
        thu_e = thu["end"]
        fri = loc["hours"]["friday"]["openIntervals"][0]
        fri_s = fri["start"]
        fri_e = fri["end"]
        sat = loc["hours"]["saturday"]["openIntervals"][0]
        sat_s = sat["start"]
        sat_e = sat["end"]
        sun = loc["hours"]["sunday"]["openIntervals"][0]
        sun_s = sun["start"]
        sun_e = sun["end"]
        mon = "Mon " + mon_s + "-" + mon_e
        tue = "Tue " + tue_s + "-" + tue_e
        wed = "Wed " + wed_s + "-" + wed_e
        thu = "Thu " + thu_s + "-" + thu_e
        fri = "Fri " + fri_s + "-" + fri_e
        sat = "Sat " + sat_s + "-" + sat_e
        sun = "Sun " + sun_s + "-" + sun_e
        hours_of_operation = (
            mon + " " + tue + " " + wed + " " + thu + " " + fri + " " + sat + " " + sun
        )
        yield SgRecord(
            locator_domain="https://www.petsuitesofamerica.com/",
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="<MISSING>",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
