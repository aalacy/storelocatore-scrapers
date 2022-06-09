from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=2500&location=AZ&limit=25&api_key=8e1b0c45f4498964c5689a5c0decbbf7&v=20181201&resolvePlaceholders=true&languages=en&entityTypes=restaurant&savedFilterIds=408126607"
    loclist = session.get(url, headers=headers).json()["response"]["entities"]

    for loc in loclist:

        title = loc["name"]
        lat = loc["cityCoordinate"]["latitude"]
        longt = loc["cityCoordinate"]["longitude"]
        street = loc["address"]["line1"]
        city = loc["address"]["city"]
        state = loc["address"]["region"]
        pcode = loc["address"]["postalCode"]
        ccode = loc["address"]["countryCode"]

        try:
            link = loc["landingPageUrl"]
        except:
            link = "<MISSING>"
        phone = loc["mainPhone"]
        hourslist = loc["hours"]
        hours = ""
        for day in hourslist:
            hr = hourslist[day]["openIntervals"][0]
            start = hr["start"] + " AM - "
            closestr = hr["end"]
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
                + " PM "
            )
        ltype = "<MISSING>"
        if "Coming Soon" in title:
            ltype = "Coming Soon"
        yield SgRecord(
            locator_domain="https://www.nextlevelburger.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=ltype,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
