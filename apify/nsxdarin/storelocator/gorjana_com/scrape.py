from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data(sgw: SgWriter):

    url = "https://gorjana.com/pages/store-locator"
    r = session.get(url, headers=headers)
    website = "gorjana.com"
    country = "US"
    typ = "<MISSING>"
    store = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    lines = r.iter_lines()
    Found = False
    for line in lines:
        line = str(line)
        if Found is False and "var storeMarkers" in line:
            Found = True
        if Found and "</script>" in line:
            Found = False
        if Found and "id: " in line:
            store = line.split("id: ")[1].split(",")[0].replace("`", "")
            g = next(lines)
            g = str(g)
            name = g.split("title: `")[1].split("`")[0]
            g = next(lines)
            g = str(g)
            if not g:
                continue
            g = g.split(": `")[1].split("`")[0]
            if not g:
                continue
            if g.count("<br />") == 0:
                add = g.split(",")[0].strip() + " " + g.split(",")[1].strip()
                city = g.split(",")[2].strip()
                state = g.split(",")[3].strip().split(" ")[0]
                zc = g.rsplit(" ", 1)[1]
            elif g.count("<br />") == 1:
                add = g.split("<br")[0]
                city = g.split("<br />")[1].split(",")[0]
                state = g.split("<br />")[1].split(",")[1].strip().split(" ")[0]
                zc = g.rsplit(" ", 1)[1]
            else:
                add = g.split("<br />")[0].strip() + " " + g.split("<br />")[1].strip()
                city = g.split("<br />")[2].split(",")[0]
                state = g.split("<br />")[2].split(",")[1].strip().split(" ")[0]
                zc = g.rsplit(" ", 1)[1]
        if Found and "phone: `" in line:
            phone = line.split("phone: `")[1].split("`")[0]
        if Found and "working_hours: `" in line:
            hours = (
                line.split("working_hours: `")[1]
                .split("`")[0]
                .replace("<br />", "; ")
                .replace("|", ":")
            )
            if hours == "":
                hours = "<MISSING>"

            if "coming soon" in name.lower():
                continue

            sgw.write_row(
                SgRecord(
                    locator_domain=website,
                    page_url=url,
                    location_name=name,
                    street_address=add,
                    city=city,
                    state=state,
                    zip_postal=zc,
                    country_code=country,
                    store_number=store,
                    phone=phone,
                    location_type=typ,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
