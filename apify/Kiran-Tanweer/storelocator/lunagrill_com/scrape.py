from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape import sgpostal as parser
import os


os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"

session = SgRequests()
website = "lunagrill_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://locations.lunagrill.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        linklist = []
        url = "https://locations.lunagrill.com/site-map/US"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        info = soup.text
        links = str(soup)
        alldata = links.split('<script defer=""')[1].split(
            "Yext.analyticsEvent = yext.analytics.getYextAnalytics("
        )[0]
        coords = alldata.split("Get Directions")
        for i in coords:
            coordslink = i.split('"drivingdirection" href="')
            if len(coordslink) == 2:
                link = coordslink[1].split('" rel="')[0]
                linklist.append(link)

        info = info.split("Get Directions")
        for j, k in zip(info, linklist):
            title = "Luna Grill"
            hours = j.split('"normalHours"')
            if len(hours) == 2:
                hours = hours[1].split(',"utcOffsets"')[0]
                mon = hours.split('"MONDAY","intervals":[{')[1].split("}],")[0]
                mon_start = mon.split('"start":')[1]
                mon_end = mon.split('"end":')[1].split(",")[0]

                tues = hours.split('"TUESDAY","intervals":[{')[1].split("}],")[0]
                tues_start = tues.split('"start":')[1]
                tues_end = tues.split('"end":')[1].split(",")[0]

                wed = hours.split('"WEDNESDAY","intervals":[{')[1].split("}],")[0]
                wed_start = wed.split('"start":')[1]
                wed_end = wed.split('"end":')[1].split(",")[0]

                thurs = hours.split('"THURSDAY","intervals":[{')[1].split("}],")[0]
                thurs_start = thurs.split('"start":')[1]
                thurs_end = thurs.split('"end":')[1].split(",")[0]

                fri = hours.split('"FRIDAY","intervals":[{')[1].split("}],")[0]
                fri_start = fri.split('"start":')[1]
                fri_end = fri.split('"end":')[1].split(",")[0]

                sat = hours.split('"SATURDAY","intervals":[{')[1].split("}],")[0]
                sat_start = sat.split('"start":')[1]
                sat_end = sat.split('"end":')[1].split(",")[0]

                sun = hours.split('"SUNDAY","intervals":[{')[1].split("}],")[0]
                sun_start = sun.split('"start":')[1]
                sun_end = sun.split('"end":')[1].split(",")[0]

                if mon_start == "1100":
                    mon_start = "11:00 AM"
                if tues_start == "1100":
                    tues_start = "11:00 AM"
                if wed_start == "1100":
                    wed_start = "11:00 AM"
                if thurs_start == "1100":
                    thurs_start = "11:00 AM"
                if fri_start == "1100":
                    fri_start = "11:00 AM"
                if sat_start == "1100":
                    sat_start = "11:00 AM"
                if sun_start == "1100":
                    sun_start = "11:00 AM"

                if mon_start == "1030":
                    mon_start = "10:30 AM"
                if tues_start == "1030":
                    tues_start = "10:30 AM"
                if wed_start == "1030":
                    wed_start = "10:30 AM"
                if thurs_start == "1030":
                    thurs_start = "10:30 AM"
                if fri_start == "1030":
                    fri_start = "10:30 AM"
                if sat_start == "1030":
                    sat_start = "10:30 AM"
                if sun_start == "1030":
                    sun_start = "10:30 AM"

                if sun_start == "1200":
                    sun_start = "12:00 PM"
                if sun_start == "0":
                    sun_start = "12:00 AM"

                if mon_end == "2100":
                    mon_end = "9:00 PM"
                if tues_end == "2100":
                    tues_end = "9:00 PM"
                if wed_end == "2100":
                    wed_end = "9:00 PM"
                if thurs_end == "2100":
                    thurs_end = "9:00 PM"
                if fri_end == "2100":
                    fri_end = "9:00 PM"
                if sat_end == "2100":
                    sat_end = "9:00 PM"
                if sun_end == "2100":
                    sun_end = "9:00 PM"

                if mon_end == "2030":
                    mon_end = "8:30 PM"
                if tues_end == "2030":
                    tues_end = "8:30 PM"
                if wed_end == "2030":
                    wed_end = "8:30 PM"
                if thurs_end == "2030":
                    thurs_end = "8:30 PM"
                if fri_end == "2030":
                    fri_end = "8:30 PM"
                if sat_end == "2030":
                    sat_end = "8:30 PM"
                if sun_end == "2030":
                    sun_end = "8:30 PM"

                if mon_end == "2000":
                    mon_end = "8:00 PM"
                if tues_end == "2000":
                    tues_end = "8:00 PM"
                if wed_end == "2000":
                    wed_end = "8:00 PM"
                if thurs_end == "2000":
                    thurs_end = "8:00 PM"
                if fri_end == "2000":
                    fri_end = "8:00 PM"
                if sat_end == "2000":
                    sat_end = "8:00 PM"
                if sun_end == "2000":
                    sun_end = "8:00 PM"
                if sun_end == "1900":
                    sun_end = "7:00 PM"

                if mon_end == "1900":
                    mon_end = "7:00 PM"
                if tues_end == "1900":
                    tues_end = "7:00 PM"
                if wed_end == "1900":
                    wed_end = "7:00 PM"
                if thurs_end == "1900":
                    thurs_end = "7:00 PM"
                if fri_end == "1900":
                    fri_end = "7:00 PM"
                if sat_end == "1900":
                    sat_end = "7:00 PM"
                if sun_end == "1800":
                    sun_end = "6:00 PM"

                if mon_end == "1930":
                    mon_end = "7:30 PM"
                if tues_end == "1930":
                    tues_end = "7:30 PM"
                if wed_end == "1930":
                    wed_end = "7:30 PM"
                if thurs_end == "1930":
                    thurs_end = "7:30 PM"
                if fri_end == "1930":
                    fri_end = "7:30 PM"
                if sat_end == "1930":
                    sat_end = "7:30 PM"
                if sun_end == "1930":
                    sun_end = "7:30 PM"

                HOO = (
                    "Monday: "
                    + mon_start
                    + " - "
                    + mon_end
                    + " "
                    + "Tuesday: "
                    + tues_start
                    + " - "
                    + tues_end
                    + " "
                    + "Wednesday: "
                    + wed_start
                    + " - "
                    + wed_end
                    + " "
                    + "Thursday: "
                    + thurs_start
                    + " - "
                    + thurs_end
                    + " "
                    + "Friday: "
                    + fri_start
                    + " - "
                    + fri_end
                    + " "
                    + "Saturday: "
                    + sat_start
                    + " - "
                    + sat_end
                    + " "
                    + "Sunday: "
                    + sun_start
                    + " - "
                    + sun_end
                )

            address = j.split("}]}")
            if len(address) == 2:
                address = address[1].split("USPhone:")[0]
                address = address.replace(",", "")
                address = address.strip()
                parsed = parser.parse_address_usa(address)
                street1 = (
                    parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
                )
                street = (
                    (street1 + ", " + parsed.street_address_2)
                    if parsed.street_address_2
                    else street1
                )
                city = parsed.city if parsed.city else "<MISSING>"
                state = parsed.state if parsed.state else "<MISSING>"
                pcode = parsed.postcode if parsed.postcode else "<MISSING>"

            phone = j.split("Phone: ")
            if len(phone) == 3:
                phone = phone[1].split("Details:")[0]
                phone = phone.strip()
            coordsurl = k
            lat = coordsurl.split("q=")[1].split(",")[0]
            lng = coordsurl.split(",")[1]

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://locations.lunagrill.com/",
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=HOO.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE},
                fail_on_empty_id=True,
            )
            .with_truncate(SgRecord.Headers.LATITUDE, 3)
            .with_truncate(SgRecord.Headers.LONGITUDE, 3)
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
