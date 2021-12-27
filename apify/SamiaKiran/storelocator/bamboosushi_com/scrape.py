import re
import json
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "bamboosushi_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://bamboosushi.com/"
MISSING = SgRecord.MISSING


def fetch_data():

    url = "https://bamboosushi.com/locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("a", string=re.compile("More Information"))
    for loc in loclist:
        page_url = DOMAIN + loc["href"]
        log.info(page_url)
        r = session.get(page_url, headers=headers)
        loc = json.loads(
            r.text.split('<script id="__NEXT_DATA__" type="application/json">')[
                1
            ].split("</script>")[0]
        )
        temp = loc["props"]["pageProps"]["fields"]
        location_name = temp["title"]
        hours = temp["hours"]["fields"]
        try:
            mo = "Mon " + hours["mondayOpen"] + "-" + hours["mondayClose"]
        except:
            mo = "Mon Closed"
        try:
            tu = " Tue " + hours["tuesdayOpen"] + "-" + hours["tuesdayClose"]
        except:
            tu = " Tue Closed"
        try:
            we = " Wed " + hours["wednesdayOpen"] + "-" + hours["wednesdayClose"]
        except:
            we = " Wed Closed"
        try:
            th = " Thu " + hours["thursdayOpen"] + "-" + hours["thursdayOpen"]
        except:
            th = " Thu Closed"
        try:
            fr = " Fri " + hours["fridayOpen"] + "-" + hours["fridayOpen"]
        except:
            fr = " Fri Closed"
        sa = " Sat " + hours["saturdayOpen"] + "-" + hours["saturdayOpen"]
        su = " Sun " + hours["sundayOpen"] + "-" + hours["sundayOpen"]
        hours_of_operation = mo + tu + we + th + fr + sa + su
        phone = temp["phone"]
        address = temp["address"].replace("\n", " ")
        address = address.replace(",", " ")
        address = usaddress.parse(address)
        i = 0
        street_address = ""
        city = ""
        state = ""
        zip_postal = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street_address = street_address + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                zip_postal = zip_postal + " " + temp[0]
            i += 1
        country_code = "US"
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=hours_of_operation,
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
