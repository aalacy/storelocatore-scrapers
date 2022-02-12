from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("tagheuer_com")


def fetch_data():
    ids = []
    countries = [
        "ad",
        "ag",
        "am",
        "ao",
        "aw",
        "az",
        "ba",
        "bb",
        "bd",
        "bg",
        "bh",
        "bi",
        "bl",
        "bm",
        "bn",
        "bo",
        "bs",
        "by",
        "bz",
        "ci",
        "cl",
        "cr",
        "cw",
        "cy",
        "do",
        "ec",
        "ee",
        "eg",
        "et",
        "fj",
        "gd",
        "ge",
        "gg",
        "gi",
        "gp",
        "gt",
        "gu",
        "hn",
        "hu",
        "ie",
        "im",
        "iq",
        "is",
        "je",
        "jm",
        "jo",
        "kh",
        "kn",
        "kw",
        "ky",
        "kz",
        "lb",
        "lc",
        "li",
        "lk",
        "lu",
        "lv",
        "ma",
        "mf",
        "mg",
        "mk",
        "mn",
        "mo",
        "mp",
        "mq",
        "mt",
        "mu",
        "mv",
        "mz",
        "nc",
        "ng",
        "np",
        "nz",
        "om",
        "pa",
        "pe",
        "ph",
        "pk",
        "pr",
        "py",
        "qa",
        "re",
        "ro",
        "rs",
        "sc",
        "si",
        "sk",
        "sm",
        "sv",
        "sx",
        "tc",
        "th",
        "tn",
        "ua",
        "uy",
        "uz",
        "ve",
        "vg",
        "vi",
        "ye",
        "ae",
        "al",
        "ar",
        "at",
        "au",
        "be",
        "br",
        "ca",
        "ch",
        "cn",
        "co",
        "cz",
        "de",
        "dk",
        "dz",
        "es",
        "fi",
        "fr",
        "gb",
        "gr",
        "hk",
        "hr",
        "id",
        "il",
        "in",
        "it",
        "jp",
        "kr",
        "mx",
        "my",
        "nl",
        "no",
        "pl",
        "pt",
        "ru",
        "sa",
        "se",
        "sg",
        "tr",
        "tw",
        "us",
        "za",
    ]
    for cc in countries:
        page = 1
        session = SgRequests()
        time.sleep(5)
        url = "https://store.tagheuer.com/" + cc + "?page=" + str(page)
        r = session.get(url, headers=headers)
        website = "tagheuer.com"
        country = cc.upper()
        logger.info("Pulling %s..." % cc)
        pages = "1"
        for line in r.iter_lines():
            if '<span class="sr-only">Pagination"</span>' in line:
                pages = (
                    line.split('<span class="sr-only">Pagination"</span>')[1]
                    .strip()
                    .replace("\t", "")
                    .replace("\r", "")
                    .replace("\n", "")
                )
        for x in range(1, int(pages) + 1):
            coords = []
            infos = []
            name = ""
            logger.info("%s, Page %s..." % (cc, str(x)))
            purl = "https://store.tagheuer.com/" + cc + "?page=" + str(x)
            session = SgRequests()
            r2 = session.get(purl, headers=headers)
            lines = r2.iter_lines()
            time.sleep(5)
            AFound = False
            for line2 in lines:
                if 'data-lf-url="' in line2:
                    curl = (
                        "https://store.tagheuer.com"
                        + line2.split('data-lf-url="')[1].split('"')[0]
                    )
                if '<span class="components-outlet-item-search-result-basic' in line2:
                    g = next(lines)
                    name = (
                        g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                    )
                    add = ""
                    city = ""
                    state = ""
                    zc = ""
                    phone = ""
                if '<a href="tel:' in line2:
                    phone = (
                        line2.split('<a href="tel:')[1].split('"')[0].replace("+", "")
                    )
                if "point.latitude" in line2 and "allPosMarker" not in line2:
                    llat = line2.split('"')[1]
                if "point.longitude " in line2 and "allPosMarker" not in line2:
                    llng = line2.split('"')[1]
                if 'point.data.id = "' in line2:
                    store = line2.split('"')[1]
                if 'point.data.posType = "' in line2:
                    typ = line2.split('point.data.posType = "')[1].split('"')[0]
                    if typ == "":
                        typ = "<MISSING>"
                    coords.append(llat + "|" + llng + "|" + store + "|" + typ)
                if 'address-basic__line"' in line2:
                    AFound = True
                    g = next(lines)
                    if ">" in g:
                        g = next(lines)
                        add = (
                            g.strip()
                            .replace("\r", "")
                            .replace("\n", "")
                            .replace("\t", "")
                        )
                if AFound and "</div>" in line2:
                    AFound = False
                if AFound and "<span" in line2:
                    g = next(lines)
                    h = next(lines)
                    city = line2.split(">")[1].split("<")[0].strip()
                    state = g.split(">")[1].split("<")[0].strip()
                    zc = h.split(">")[1].split("<")[0].strip()
                if AFound and "<br />" in line2:
                    add = (
                        add
                        + " "
                        + line2.split("<br />")[1]
                        .strip()
                        .replace("\t", "")
                        .replace("\n", "")
                        .replace("\r", "")
                    )
                if '<div class="components-outlet-item-search-result-basic"' in line2:
                    if name != "":
                        infos.append(
                            name
                            + "|"
                            + curl
                            + "|"
                            + add
                            + "|"
                            + city
                            + "|"
                            + state
                            + "|"
                            + zc
                            + "|"
                            + phone
                        )
                if (
                    '<div class="search-full__pan__results-container__results__infos">'
                    in line2
                ):
                    infos.append(
                        name
                        + "|"
                        + curl
                        + "|"
                        + add
                        + "|"
                        + city
                        + "|"
                        + state
                        + "|"
                        + zc
                        + "|"
                        + phone
                    )
            for y in range(0, len(infos)):
                name = infos[y].split("|")[0]
                loc = infos[y].split("|")[1]
                add = infos[y].split("|")[2]
                city = infos[y].split("|")[3]
                state = infos[y].split("|")[4]
                zc = infos[y].split("|")[5]
                phone = infos[y].split("|")[6]
                lat = coords[y].split("|")[0]
                lng = coords[y].split("|")[1]
                store = coords[y].split("|")[2]
                typ = coords[y].split("|")[3]
                hours = "<MISSING>"
                if state == "":
                    state = "<MISSING>"
                if zc == "":
                    zc = "<MISSING>"
                if country == "US":
                    if " " in zc:
                        zc = zc.rsplit(" ", 1)[1].strip()
                if store not in ids:
                    ids.append(store)
                    if phone == "":
                        phone = "<MISSING>"
                    if "144998-ahmed-seddiqi-sons-city-centre-mirdif" in loc:
                        add = "City Centre Mirdif Dubai"
                    if "144978-ahmed-seddiqi-sons-dubai-festival-city" in loc:
                        add = "Dubai Festival City Dubai"
                    if "144970-ahmed-seddiqi-sons-mall-of-the-emirates" in loc:
                        add = "Mall Of The Emirates Dubai"
                    if "144971-ahmed-seddiqi-sons-wafi-shopping-mall" in loc:
                        add = "Wafi Shopping Mall Dubai"
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
