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

    daylist = ["mon", "tues", "wednes", "thurs", "fri", "satur", "sun"]
    url = "https://shipleydonuts.com/locations/"
    r = session.get(url, headers=headers)
    loclist = r.text.split("locations_meta = ", 1)[1].split("];", 1)[0]
    loclist = loclist + "]"
    loclist = json.loads(loclist)
    for loc in loclist:

        store = loc["address"]["store_number"]
        lat = loc["map_pin"]["lat"]
        longt = loc["map_pin"]["lng"]
        state = loc["map_pin"]["state_short"]
        try:
            city = loc["map_pin"]["city"]
        except:
            city = "<MISSING>"
        try:
            pcode = loc["map_pin"]["post_code"]
        except:
            pcode = loc["map_pin"]["address"].split(state + " ", 1)[1].split(",", 1)[0]
        store = loc["address"]["store_number"]
        street = (
            loc["address"]["address_line_1"]
            + " "
            + str(loc["address"]["address_line_2"])
        )
        ltype = "<MISSING>"
        if "Coming Soon" in street:
            ltype = "Coming Soon"
        phone = loc["branch_information"]["phone_number"]
        link = loc["single_page"]
        hourlist = loc["opening_hours"]
        hours = ""
        for day in daylist:
            hours = hours + day + "day " + hourlist[day + "day_opening_hours"] + " "
        yield SgRecord(
            locator_domain="https://shipleydonuts.com",
            page_url=link,
            location_name="Shipley Do-Nuts",
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=ltype,
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
