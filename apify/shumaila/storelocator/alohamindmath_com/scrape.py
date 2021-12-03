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

    url = "https://alohamindmath.com/wp-admin/admin-ajax.php?action=get_center_locations&formattedAddress=&boundsNorthEast=&boundsSouthWest="
    loclist = session.get(url, headers=headers).json()

    for loc in loclist:

        store = loc["id"]
        title = loc["name"]
        street = loc["address"] + " " + loc["address2"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["postal"]
        lat = loc["lat"]
        longt = loc["lng"]
        phone = loc["phone"]
        link = loc["web"]
        if "Dr Suite" in city or "1020 " in city:
            temp = title.split(",", 1)[0]
            if temp in city:
                street = street + " " + city.replace(temp, "")
            else:
                street = street + " " + city
            city = temp
        yield SgRecord(
            locator_domain="https://alohamindmath.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.replace(",", "").strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
