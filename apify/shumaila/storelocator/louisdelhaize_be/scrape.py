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

    url = "https://magasins.louisdelhaize.be/fr"
    r = session.get(url, headers=headers)
    loclist = r.text.split('"@graph": ', 1)[1].split("}]}]", 1)[0]
    loclist = loclist + "}]}]"

    loclist = json.loads(loclist.strip())
    for loc in loclist:

        title = loc["name"]
        link = loc["url"]
        phone = loc["telephone"]
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        pcode = loc["address"]["postalCode"]
        ccode = loc["address"]["addressCountry"]
        lat = loc["geo"]["latitude"]
        longt = loc["geo"]["longitude"]
        hourslist = loc["openingHoursSpecification"]
        hours = ""
        for hr in hourslist:
            day = hr["dayOfWeek"]
            start = hr["opens"] + " am - "
            closestr = hr["closes"]
            close = int(closestr.split(":", 1)[0])
            if close > 12:
                close = close - 12
            hours = (
                hours
                + day
                + " "
                + start
                + str(close)
                + ":"
                + closestr.split(":", 1)[1]
                + " pm "
            )
        yield SgRecord(
            locator_domain="https://louisdelhaize.be/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=SgRecord.MISSING,
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=SgRecord.MISSING,
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
