from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.carlsjr.ca/locations"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    lines = r.iter_lines(decode_unicode=True)
    HFound = False
    for line in lines:
        if 'style="color:#FFC72C;">' in line or '<span style="color:#FFC72C">' in line:
            state = (
                line.split('<span style="color:#')[1]
                .split(">")[1]
                .split("<")[0]
                .strip()
            )
        if (
            "</span></span></span></p></div></div></div></div>" in line
            and "<footer" not in line
        ):
            name = line.split('<span style="color:#2D2926">')[1].split("<")[0].strip()
            country = "CA"
            loc = "<MISSING>"
            typ = "Restaurant"
            store = "<MISSING>"
            city = "<INACCESSIBLE>"
            hours = ""
            zc = "<INACCESSIBLE>"
            website = "carlsjr.ca"
            lat = "<MISSING>"
            lng = "<MISSING>"
            addinfo = line.split('procn">')[2]
            if '<span style="color:#2D2926">' in addinfo:
                add = addinfo.split('<span style="color:#2D2926">')[1].split("<")[0]
            else:
                add = line.split('procn">')[2].split("<")[0].strip()
            next(lines)
            g = next(lines)
            if "HOURS:" in g:
                HFound = True
                hours = (
                    g.split("HOURS:")[1].split("<")[0].strip().replace("&nbsp;", " ")
                )
            else:
                if "PH:" in g:
                    phone = g.split("PH:")[1].split("<")[0].strip()
                else:
                    phone = "<MISSING>"
        if '">HOURS:' in line:
            HFound = True
            hours = (
                line.split('">HOURS:')[1].split("<")[0].strip().replace("&nbsp;", " ")
            )
        if HFound and '<path d="M1.6' in line:
            HFound = False
            hours = hours.replace("&amp;", "&").replace("&ndash;", "-")
            add = add.replace("&nbsp;", " ").strip()
            state2 = state
            if "PRINCE GEORGE" in name:
                state2 = "BRITISH COLUMBIA"
            if "Calgary" in add:
                state2 = "ALBERTA"
                add = add.split(",")[0]
            if "Edmonton" in add:
                add = add.split(",")[0]
            yield SgRecord(
                locator_domain=website,
                page_url=loc,
                location_name=name,
                street_address=add,
                city=city,
                state=state2,
                zip_postal=zc,
                country_code=country,
                phone=phone,
                location_type=typ,
                store_number=store,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )
        if HFound and "window.firstPageId" in line:
            HFound = False
            hours = hours.replace("&amp;", "&").replace("&ndash;", "-")
            add = add.replace("&nbsp;", " ").strip()
            state2 = state
            if "PRINCE GEORGE" in name:
                state2 = "BRITISH COLUMBIA"
            if "Calgary" in add:
                state2 = "ALBERTA"
                add = add.split(",")[0]
            if "Edmonton" in add:
                add = add.split(",")[0]
            yield SgRecord(
                locator_domain=website,
                page_url=loc,
                location_name=name,
                street_address=add,
                city=city,
                state=state2,
                zip_postal=zc,
                country_code=country,
                phone=phone,
                location_type=typ,
                store_number=store,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )
        if HFound and '">HOURS:' not in line and 'procn">' in line:
            hours = hours + "; " + line.split('procn">')[1].split("<")[0]


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
