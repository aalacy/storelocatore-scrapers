from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("allbirds_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.allbirds.com/pages/stores"
    r = session.get(url, headers=headers)
    lines = r.iter_lines()
    website = "allbirds.com"
    store = "<MISSING>"
    purl = " https://www.allbirds.com/pages/stores"
    lat = "<MISSING>"
    lng = "<MISSING>"
    typ = "Store"
    name = ""
    Intl = False
    for line in lines:
        if "Auckland" in line:
            Intl = True
        if '<h2 class="Typography--secondary-heading Typography--with-margin">' in line:
            name = line.split('">')[1].split("<")[0]
            lat = "<MISSING>"
            lng = "<MISSING>"
            hours = ""
        if "see map</a></p>" in line.lower():
            murl = line.split('href="')[1].split('"')[0]
            r2 = session.get(murl, headers=headers)
            lat = str(r2.url).split("@")[1].split(",")[0]
            lng = str(r2.url).split("@")[1].split(",")[1]
        if "location</h3>" in line.lower():
            g = next(lines)
            h = next(lines)
            if "suite" in h.lower():
                h = next(lines)
            add = g.split('">')[1].split("<")[0].strip()
            city = h.split(",")[0].strip()
            try:
                state = h.split(",")[1].strip().split(" ")[0].strip()
            except:
                state = "<MISSING>"
            if ", Paramus, NJ" in g:
                add = g.split(",")[0]
                city = "Paramus"
                state = "NJ"
                zc = "07652"
                lat = "40.9176318"
                lng = "-74.0780812"
            else:
                zc = h.split("<")[0].rsplit(" ", 1)[1].strip()
            if Intl is False:
                country = "US"
            else:
                country = "<MISSING>"
        if "day: " in line.lower() or "Saturday " in line:
            try:
                hrs = line.split('h">')[1].split("<")[0].strip()
            except:
                hrs = line.split("<")[0].strip()
            if hours == "":
                hours = hrs
            else:
                hours = hours + "; " + hrs
        if "China" in line:
            country = "CN"
        if ", China" in line:
            zc = line.split(", China")[1].split("<")[0].strip()
        if ", Japan" in line:
            zc = line.split(", Japan")[1].split("<")[0].strip()
        if "Phone</h3>" in line:
            g = next(lines)
            phone = g.split('">')[1].split("<")[0].strip()
        if '<div class="StoresPageSection">' in line or '<div class="Footer">' in line:
            if name != "":
                logger.info(name)
                if name == "Austin":
                    add = "1011 S Congress Ave, Bldg 1, Ste. 120"
                    city = "Austin"
                    state = "TX"
                    zc = "78704"
                if "219 N 2nd" in add:
                    zc = "55401"
                if "Auckland" in name:
                    country = "NZ"
                if "London" in name:
                    country = "GB"
                if "Amsterdam" in name:
                    country = "NL"
                if "Tokyo" in name:
                    country = "JP"
                if "Berlin" in name:
                    country = "DE"
                if "<" in add:
                    add = add.split("<")[0]
                if country == "CN":
                    state = "<MISSING>"
                if "M39(B1MS-15)" in add:
                    zc = "610021"
                    add = "M39(B1MS-15) No. 8, Shamao St"
                    city = "Chengdu"
                if "SLG23" in add:
                    add = "SLG23 (South LG1, Unit 23) Nr. 19, Sanlitun Rd"
                    city = "Beijing"
                if "Harajuku" in name:
                    add = "1F Jingu No Mori Building, 1-14-34, Jungumae, Shibuya-ku"
                    city = "Tokyo"
                if "Marunouchi" in name:
                    add = "#105 Shin Kokusai Building, 3-4-1 Marunouchi, Chiyoda-ku"
                    city = "Tokyo"
                if "MU47a" in add:
                    add = "MU47a No.383 Tianhe Rd"
                    city = "Guangzhou"
                if "London" in city:
                    zc = city.split("London")[1].strip()
                    city = "London"
                    state = "<MISSING>"
                if "Auckland" in city:
                    zc = city.split("Auckland")[1].strip()
                    city = "Auckland"
                if "Amsterdam" in city:
                    city = "Amsterdam"
                    zc = "1016 BZ"
                if "Berlin" in city:
                    zc = city.split("Berlin")[0].strip()
                    city = "Berlin"
                if "L241" in add:
                    add = "L241, Nr. 789 West Nanjing Rd"
                    city = "Shanghai"
                    country = "CN"
                    zc = "200000"
                if "Seoul" in name:
                    add = "45 Gangnam-daero 160-gil, Sinsa-dong"
                    city = "Seoul"
                    state = "<MISSING>"
                    country = "KR"
                    zc = "<MISSING>"
                if "<" in zc and zc != "<MISSING>":
                    zc = zc.split("<")[0].strip()
                if "675 Ponce de Leon" in add:
                    add = add + " Suite W115B"
                    zc = "30308"
                if "660 Stanford Shopping Center" in add:
                    add = add + " Room #9"
                    zc = "94304"
                if len(state) == 2:
                    country = "US"
                if "SF Premium" in add:
                    add = "3228 Livermore Outlets Drive"
                if "660 Stanford" in add:
                    hours = "Mon-Thu: 11am-7pm; Fri-Sat: 10am-7pm; Sun: 12pm-6pm"
                if "77 West" in add:
                    hours = "Mon-Sat: 10am-8pm; Sun: 11am-7pm"
                if "Suite 1985," in add:
                    add = add.replace("1985,", "1985")
                if "10250 Santa" in add:
                    hours = "Mon-Sat: 10am-9pm; Sun: 11am-8pm"
                if "219 N" in add:
                    hours = "Mon-Sat: 10am-7pm; Sun: 11am-6pm"
                if "Center," in add:
                    add = add.replace("Center,", "Center")
                if "1st Ave," in add:
                    add = add.replace("1st Ave,", "1st Ave")
                if "Strasse 28," in add:
                    add = add.replace("Strasse 28,", "Strasse 28")
                if city == "Paramus":
                    add = "One Garden State Plaza"
                if country == "KR" or country == "CN" or country == "JP":
                    if "98616" in phone:
                        phone = "<MISSING>"
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
