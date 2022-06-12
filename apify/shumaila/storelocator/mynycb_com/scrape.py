from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://www.mynycb.com/api/async/branches"

    loclist = session.get(url, headers=headers).json()
    loclist = json.loads(loclist)

    for loc in loclist:
        title = loc["Group"]["Name"]
        store = loc["Services"][0]["LocationId"]
        lat = loc["Latitude"]
        longt = loc["Longitude"]
        street = loc["AddressLine1"] + " " + str(loc["AddressLine2"])
        street = street.replace("None", "").strip()
        city = loc["City"]
        state = loc["StateCode"]
        pcode = loc["PostalCode"]
        ccode = "US"
        phone = loc["Phone"]
        hourslist = loc["LocationHours"]
        hours = ""
        for hr in hourslist:
            if "Branch Services" in hr["ServiceName"]:
                try:
                    start = (
                        hr["StartTime"].split(":")[0]
                        + ":"
                        + hr["StartTime"].split(":")[1]
                        + " AM - "
                    )
                    end = (int)(hr["EndTime"].split(":")[0])
                    if end > 12:
                        end = end - 12
                    endtime = str(end) + ":" + hr["EndTime"].split(":")[1] + " PM  "
                    hours = hours + hr["Weekday"] + " " + start + endtime
                except:
                    hours = hours + hr["Weekday"] + " Closed "
        if len(hours) < 3:
            hours = "<MISSING>"
        if "ATM" in loc["Type"]["Name"]:
            ltype = "ATM"
            hours = "<MISSING>"
            phone = "<MISSING>"
        else:
            ltype = "Branch"
        if title.find("Coming Soon") == -1:

            yield SgRecord(
                locator_domain="https://www.mynycb.com/",
                page_url="https://www.mynycb.com/BranchLocator/Index",
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=str(store),
                phone=phone.strip(),
                location_type=ltype,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
