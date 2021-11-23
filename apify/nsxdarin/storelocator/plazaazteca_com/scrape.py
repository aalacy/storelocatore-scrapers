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
    locs = []
    url = "https://plazaazteca.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    website = "plazaazteca.com"
    country = "US"
    linesone = r.iter_lines()
    for line in linesone:
        line = str(line.decode("utf-8"))
        if (
            '<h2 class="elementor-heading-title elementor-size-default"><a href="'
            in line
        ):
            lurl = line.split(
                '<h2 class="elementor-heading-title elementor-size-default"><a href="'
            )[1].split('"')[0]
            if "COMING SOON" in line:
                lurl = "CS"
        if '<div class="elementor-text-editor elementor-clearfix">' in line:
            g = next(linesone)
            g = str(g.decode("utf-8"))
            try:
                a5 = g.split('">(')[1].split("<")[0]
            except:
                pass
            try:
                a5 = g.split(';">(')[1].split("<")[0]
            except:
                pass
            if (
                '</p><p><span style="font-size: 15px;">' not in g
                and '</p><p class="p1"><span style="font-size: 15px;">' not in g
            ):
                a1 = g.split(">")[1].split("<")[0].replace(",", "")
                a2 = g.split("</p><p>")[1].split(",")[0]
                a3 = g.split("</p><p>")[1].split("<")[0].split(",")[1].strip()
                a4 = g.split("</p><p>")[1].split("<")[0].strip().rsplit(" ", 1)[1]
                try:
                    a5 = g.split("</p><p>")[2].split("<")[0].strip()
                except:
                    a5 = "<MISSING>"
            else:
                a1 = g.split(">")[1].split("<")[0].replace(",", "")
                try:
                    a2 = g.split('</p><p><span style="font-size: 15px;">')[1].split(
                        ","
                    )[0]
                except:
                    a2 = g.split('</p><p class="p1"><span style="font-size: 15px;">')[
                        1
                    ].split(",")[0]
                a3 = g.split('</span><span style="font-size: 15px;">')[1].split(",")[0]
                a4 = (
                    g.split('</span><span style="font-size: 15px;">')[2]
                    .split("<")[0]
                    .strip()
                )
            if lurl != "CS":
                locs.append(lurl + "|" + a1 + "|" + a2 + "|" + a3 + "|" + a4 + "|" + a5)
    for loc in locs:
        store = "<MISSING>"
        name = ""
        add = loc.split("|")[1]
        city = loc.split("|")[2]
        state = loc.split("|")[3]
        zc = loc.split("|")[4]
        purl = loc.split("|")[0]
        phone = loc.split("|")[5]
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        typ = "<MISSING>"
        r2 = session.get(purl, headers=headers, verify=False)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("&")[0].strip()
                if "|" in name:
                    name = name.split("|")[0].strip()
            if "DAY" in line2 and "</span>" in line2:
                day = line2.split("</span>")[0].strip().replace("\t", "")
                next(lines)
                next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                hrs = day + ": " + g.split("</p>")[0].strip().replace("\t", "")
                hrs = hrs.replace(
                    '<span style="font-size: 27px; font-style: normal; font-weight: 500;">',
                    "",
                ).replace("</span>", "")
                hrs = hrs.replace(
                    '<span style=""font-size: 27px; font-style: normal;"">', ""
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "www.toroazteca.com" in loc:
                add = "194 Buckland Hills Drive Suite 1052"
                city = "Manchester"
                state = "Connecticut"
                zc = "06042"
                phone = "860-648-4454"
                hours = "Monday - Thursday: 11am - 10pm (Bar Open Late); Friday - Saturday: 11am - 11pm (Bar Open Late); Sunday: 11:30am - 10pm (Bar Open Late)"
            if "<" in name:
                name = name.split("<")[0]
        if "Coming Soon" not in name:
            if hours == "":
                hours = "<MISSING>"
            if "allentown" in purl:
                phone = "(484) 656 7277"
            if "granby" in purl:
                hours = "MONDAY - FRIDAY: 11AM - 2:30PM, 4:30PM - 10PM; SATURDAY: 12PM - 2:30PM, 4:30PM - 10PM; SUNDAY: 12PM - 2:30PM, 4:30PM - 9PM"
            if "state-college" in purl:
                hours = "MONDAY - SATURDAY: 11AM - 10PM; SUNDAY: 11AM - 9PM"
            yield SgRecord(
                locator_domain=website,
                page_url=purl,
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
