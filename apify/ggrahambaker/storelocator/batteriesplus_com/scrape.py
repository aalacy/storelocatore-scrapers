import re
import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    pattern = re.compile(r"\s\s+")

    url = "https://maps.stores.batteriesplus.com.prod.rioseo.com/api/getAsyncLocations?template=search&level=search&radius=5000"
    loclist = session.get(url, headers=headers).json()["maplist"]
    loclist = loclist.split(">{", 1)[1].split("<", 1)[0].split("},{")

    for loc in loclist:
        loc = "{" + loc + "}"
        try:
            loc = json.loads(re.sub(pattern, " ", loc).strip())
        except:
            loc = json.loads(re.sub(pattern, " ", loc[0 : len(loc) - 2]).strip())
        street = loc["address_1"] + " " + str(loc["address_2"])
        store = loc["lid"]
        city = loc["city"]
        state = loc["region"]
        pcode = loc["post_code"]
        title = loc["location_name"] + " " + city + ", " + state + " # " + str(store)
        link = loc["url"]
        lat = loc["lat"]
        longt = loc["lng"]
        phone = loc["local_phone"]
        ccode = loc["country"]
        try:
            hourslist = json.loads(loc["hours_sets:primary"])["days"]
            hours = ""
            for day in hourslist:
                try:
                    closestr = hourslist[day][0]["close"]
                    close = int(closestr.split(":", 1)[0])
                    if close > 12:
                        close = close - 12
                    hours = (
                        hours
                        + day
                        + " "
                        + hourslist[day][0]["open"]
                        + " am - "
                        + str(close)
                        + ":"
                        + str(closestr.split(":", 1)[1])
                        + " pm "
                    )
                except:
                    hours = hours + day + " " + hourslist[day] + " "
        except:
            hours = "<MISSING>"
            if "Opening" in loc["location_alert_message"]:
                hours = "Coming Soon"
        yield SgRecord(
            locator_domain="https://www.batteriesplus.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
