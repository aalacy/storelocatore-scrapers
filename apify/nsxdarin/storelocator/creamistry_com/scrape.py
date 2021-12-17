from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://creamistry.com/locations"
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'class="stroe_link" href="' in line:
            lurl = "https://creamistry.com/" + line.split('href="')[1].split('"')[0]
            if "detail" not in lurl:
                locs.append(lurl)
    for loc in locs:
        name = ""
        add = ""
        city = ""
        state = ""
        store = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        country = ""
        zc = ""
        phone = ""
        website = "creamistry.com"
        typ = "Restaurant"
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if (
                '<h2 class="section-title" style="padding-left:0px !important;">'
                in line2
            ):
                name = line2.split(
                    '<h2 class="section-title" style="padding-left:0px !important;">'
                )[1].split("<")[0]
            if "<h4>Address & Phone</h4>" in line2:
                g = next(lines)
                h = next(lines)
                add = g.split(">")[1].split("<")[0].strip()
                try:
                    csz = g.split("<br")[1].split(">")[1].split("<")[0]
                except:
                    csz = g.split("</br")[1].split(">")[1].split("<")[0]
                city = csz.split(",")[0]
                state = csz.split(",")[1].strip().split(" ")[0]
                zc = csz.rsplit(" ", 1)[1]
                country = "US"
                phone = h.split(">")[1].split("<")[0]
            if "var latitude = " in line2:
                lat = line2.split("var latitude = ")[1].split(";")[0]
            if "var longitude = " in line2:
                lng = line2.split("var longitude = ")[1].split(";")[0]
            if "Store Hours</h4>" in line2:
                g = next(lines)
                h = next(lines)
                if '<p class="mb-0" >' in g:
                    hours = (
                        g.split('<p class="mb-0" >')[1]
                        .split("</p>")[0]
                        .replace("</span>", "")
                        .replace("</br>", ";")
                        .replace("  ", " ")
                    )
                if '<p class="mb-0" >' in h:
                    hours = (
                        hours
                        + "; "
                        + h.split('<p class="mb-0" >')[1]
                        .split("</p>")[0]
                        .replace("</span>", "")
                        .replace("</br>", ";")
                        .replace("  ", " ")
                    )
        if "Soon" not in hours:
            if phone == "":
                phone = "<MISSING>"
            hours = hours.replace("<span>", "").replace("  ", " ")
            yield SgRecord(
                locator_domain=website,
                page_url=loc,
                location_name=name,
                street_address=add,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country,
                phone=phone,
                location_type=typ,
                store_number=store,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
