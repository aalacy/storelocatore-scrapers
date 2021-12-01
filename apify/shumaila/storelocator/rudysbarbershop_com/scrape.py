import re
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
    url = "https://rudysbarbershop.com/pages/locations"
    r = session.get(url, headers=headers)
    loclist = r.text.split("window.locations = ", 1)[1].split("];", 1)[0]
    loclist = re.sub(pattern, "", loclist).strip()
    loclist = loclist.replace("[{", "").split("}")
    for loc in loclist:
        try:
            store = loc.split("id: ", 1)[1].split(",", 1)[0]
        except:
            break
        title = loc.split('name: "', 1)[1].split('"', 1)[0]
        address = loc.split("address: ", 1)[1].split("phone:", 1)[0]
        city = loc.split('city: "', 1)[1].split('"', 1)[0]
        link = "https://rudysbarbershop.com" + loc.split('url: "', 1)[1].split('"', 1)[
            0
        ].replace("\\", "")
        if "null" in address:
            street = pcode = state = "<MISSING>"
            if "portland" in link and "oregon" in city:
                state = "OR"
                city = "Portland"
            elif "seattle" in city:
                state = "WA"
            elif "seattle" in city:
                state = "WA"
            elif "arizona" in city:
                state = "AZ"
                if "phoenix" in link:
                    city = "Phoenix"
                elif "gilbert" in link:
                    city = "Gilbert"
        else:
            street, city = address.replace('"', "").split("\\u003cbr\\u003e", 1)
            city, state = city.split(", ", 1)
            state, pcode = state.split(" ", 1)
            if "\\u003cbr\\u003e" in city:
                temp = city
                city = city.split("\\u003cbr\\u003e")[-1]
                street = (
                    street
                    + " "
                    + temp.replace(city, "").replace("\\u003cbr\\u003e", " ").strip()
                )
        phone = loc.split("phone: ", 1)[1].split(",", 1)[0]
        hours = loc.split("hours: ", 1)[1].split("url", 1)[0]
        if "null" in hours:
            hours = "<MISSING>"
        else:
            hours = hours.replace('"', "").split("\\u003cbr\\u003e")[-1]
        hours = hours.replace("\\u0026", "-").replace(",", "")
        if "change daily" in hours:
            hours = "Temporarily Closed"
        if "null" in phone:
            phone = "<MISSING>"
        else:
            phone = phone.replace('"', "")
        lat = loc.split('latitude: "', 1)[1].split('"', 1)[0]
        longt = loc.split('longitude: "', 1)[1].split('"', 1)[0]

        yield SgRecord(
            locator_domain="https://rudysbarbershop.com/",
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
