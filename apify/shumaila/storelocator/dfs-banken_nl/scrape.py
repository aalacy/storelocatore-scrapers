from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
}


def fetch_data():

    daylist = ["mon", "tues", "wednes", "thurs", "fri", "satur", "sun"]
    url = "https://www.dfs-banken.nl/wcs/resources/store/10701/stores?langId=31"
    loclist = session.get(url, headers=headers).json()["stores"]
    for loc in loclist:

        store = loc["storeNumber"]
        street = loc["address"]["line1"] + " " + str(loc["address"]["line2"])
        street = street.replace(" None", "")
        city = loc["address"]["city"]
        ccode = loc["address"]["countryCode"]
        pcode = loc["address"]["postalCode"]
        lat = loc["yextRoutableCoordinate"]["latitude"]
        longt = loc["yextRoutableCoordinate"]["longitude"]
        phone = loc["mainPhone"]
        link = "https://www.dfs-banken.nl/store-directory/" + loc["seoToken"]
        title = loc["storeName"]
        hourslist = loc["hours"]
        hours = ""
        for day in daylist:
            day = day + "day"
            hr = hourslist[day]
            openstr = hr["openIntervals"][0]["start"] + " AM - "
            closestr = hr["openIntervals"][0]["end"]
            close = int(closestr.split(":", 1)[0])
            if close > 12:
                close = close - 12
            hours = (
                hours
                + day
                + " "
                + openstr
                + str(close)
                + ":"
                + closestr.split(":", 1)[1]
                + " PM "
            )
        yield SgRecord(
            locator_domain="https://www.dfs-banken.nl/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state="<MISSING>",
            zip_postal=pcode,
            country_code=ccode,
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours.replace(" â€¦", "").strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS}),
            duplicate_streak_failure_factor=5,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
