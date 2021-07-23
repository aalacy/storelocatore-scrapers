import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("tagheuer_com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    ids = []
    countries = [
        "ar",
        "au",
        "at",
        "be",
        "br",
        "ca",
        "cn",
        "co",
        "hr",
        "cz",
        "dk",
        "fi",
        "fr",
        "de",
        "gr",
        "hk",
        "in",
        "id",
        "il",
        "it",
        "jp",
        "my",
        "mx",
        "nl",
        "no",
        "pl",
        "pt",
        "ru",
        "sa",
        "sg",
        "za",
        "kr",
        "es",
        "se",
        "ch",
        "tw",
        "tr",
        "ae",
        "gb",
        "us",
    ]
    for cc in countries:
        page = 1
        url = "https://store.tagheuer.com/" + cc + "?page=" + str(page)
        r = session.get(url, headers=headers)
        website = "tagheuer.com"
        country = cc.upper()
        logger.info("Pulling %s..." % cc)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
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
            r2 = session.get(purl, headers=headers)
            lines = r2.iter_lines()
            AFound = False
            for line2 in lines:
                line2 = str(line2.decode("utf-8"))
                if 'data-lf-url="' in line2:
                    curl = (
                        "https://store.tagheuer.com"
                        + line2.split('data-lf-url="')[1].split('"')[0]
                    )
                if '<span class="components-outlet-item-search-result-basic' in line2:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
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
                    coords.append(llat + "|" + llng + "|" + store + "|" + typ)
                if 'address-basic__line"' in line2:
                    AFound = True
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                    if ">" in g:
                        g = next(lines)
                        g = str(g.decode("utf-8"))
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
                    g = str(g.decode("utf-8"))
                    h = str(h.decode("utf-8"))
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
                    '<div class="components-outlet-item-search-result-basic"' in line2
                    and '<div class="search-full__pan__results-container__results__infos">'
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
                    yield [
                        website,
                        loc,
                        name,
                        add,
                        city,
                        state,
                        zc,
                        country,
                        store,
                        phone,
                        typ,
                        lat,
                        lng,
                        hours,
                    ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
