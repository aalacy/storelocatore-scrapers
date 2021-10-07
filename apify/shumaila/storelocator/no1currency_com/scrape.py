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

    url = "https://api.fexcocunet.com/bureaumobileweb/rest/bureau/map/country/UK"
    loclist = session.get(url, headers=headers).json()["wrappedObject"]
    week = ["mon", "tues", "wednes", "thurs", "fri", "satur", "sun"]
    for loc in loclist:
        title = loc["name"]
        street = loc["address"]["address1"]
        city = loc["address"]["address2"]
        pcode = loc["address"]["city"]
        state = str(loc["address"]["county"]["name"])
        if len(state) < 3:
            state = "<MISSING>"
        phone = loc["address"]["telephone"]
        link = loc["address"]["websiteAddress"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        hourslist = loc["openingHours"]
        hours = ""
        for hr in week:
            day = hr + "day"
            try:
                openstr = hourslist[day + "Open"] + " AM - "

                closestr = ""
                try:
                    if int(hourslist[day + "Close"].split(":", 1)[0]) > 12:
                        closestr = (
                            str(int(hourslist[day + "Close"].split(":", 1)[0]) - 12)
                            + ":"
                            + hourslist[day + "Close"].split(":", 1)[1]
                            + " PM "
                        )
                    else:
                        closestr = hourslist[day + "Close"] + " PM "
                except:
                    pass
                hours = hours + day + " " + openstr + closestr
            except:
                hours = hours + day + " Closed "
        yield SgRecord(
            locator_domain="https://www.no1currency.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="GB",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
