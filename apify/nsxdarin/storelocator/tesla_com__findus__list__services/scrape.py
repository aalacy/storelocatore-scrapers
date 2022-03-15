# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("tesla_com__findus__list__services")

usstates = [
    "AK",
    "AL",
    "AR",
    "AS",
    "AZ",
    "CA",
    "CO",
    "CT",
    "DC",
    "DE",
    "FL",
    "GA",
    "GU",
    "HI",
    "IA",
    "ID",
    "IL",
    "IN",
    "KS",
    "KY",
    "LA",
    "MA",
    "MD",
    "ME",
    "MI",
    "MN",
    "MO",
    "MP",
    "MS",
    "MT",
    "NC",
    "ND",
    "NE",
    "NH",
    "NJ",
    "NM",
    "NV",
    "NY",
    "OH",
    "OK",
    "OR",
    "PA",
    "PR",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UM",
    "UT",
    "VA",
    "VI",
    "VT",
    "WA",
    "WI",
    "WV",
    "WY",
]
castates = [
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NT",
    "NS",
    "NU",
    "ON",
    "PE",
    "PEI",
    "QC",
    "SK",
    "YT",
]


def fetch_data():
    locs = []
    session = SgRequests()
    url = "https://www.tesla.com/findus/list"
    r = session.get(url, headers=headers)
    website = "tesla.com/findus/list/services"
    typ = "<MISSING>"
    logger.info("Pulling Stores")
    states = []
    for line in r.iter_lines():
        if '<a href="/findus/list/services/' in line:
            states.append(
                "https://www.tesla.com" + line.split('href="')[1].split('"')[0]
            )
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if '<a href="/findus/location/service/' in line2:
                lurl = "https://www.tesla.com" + line2.split('href="')[1].split('"')[0]
                locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        typ = ""
        country = ""
        state = ""
        zc = ""
        CS = False
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        HFound = True
        locality = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<span class="locality">' in line2:
                locality = (
                    line2.split('<span class="locality">')[1].split("<")[0].strip()
                )
            if '<span class="coming-soon">Coming Soon</span>' in line2:
                CS = True
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if '<span class="street-address">' in line2:
                rawadd = line2.split('<span class="street-address">')[1].split("<")[0]
            if '<span class="extended-address">' in line2:
                rawadd = (
                    rawadd
                    + " "
                    + line2.split('<span class="extended-address">')[1].split("<")[0]
                )
                rawadd = rawadd.strip()
            if '<span class="locality">' in line2:
                g = line2.replace("  ", " ").replace("  ", " ")
                rawadd = rawadd + " " + g.split('ity">')[1].split("<")[0]
                if "<br />" in g:
                    rawadd = rawadd + " " + g.split("<br />")[1].split("<")[0]
            if '<span class="type">' in line2:
                if typ == "":
                    typ = line2.split('<span class="type">')[1].split("<")[0]
                else:
                    typ = (
                        typ + ", " + line2.split('<span class="type">')[1].split("<")[0]
                    )
                if phone == "":
                    phone = line2.split('<span class="value">')[1].split("<")[0]
            if '<a href="https://maps.google.com/maps?daddr=' in line2:
                lat = line2.split('<a href="https://maps.google.com/maps?daddr=')[
                    1
                ].split(",")[0]
                lng = (
                    line2.split('<a href="https://maps.google.com/maps?daddr=')[1]
                    .split(",")[1]
                    .split('"')[0]
                )
            if "Hours</strong>" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong>")[1]
                    .replace("<br />", "; ")
                    .replace("<br/>", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong>" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong>")[1]
                    .replace("<br/>", "; ")
                    .replace("<br />", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong>" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                if "day" not in g:
                    g = next(lines)
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                HFound = False
            if "Hours</strong>" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                if "day" not in g:
                    g = next(lines)
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                HFound = False
        if "; <p>" in hours:
            hours = hours.split("; <p>")[0]
        if hours == "":
            hours = "<MISSING>"
        hours = hours.replace(";;", ";")
        if "aucklandponsonby" in loc:
            rawadd = "501 Karangahape Road"
        if "christchurch" in loc:
            rawadd = "17 Avenger Crescent, Wigram"
        if "macauservice" in loc:
            rawadd = "The Venetian, Macao Level LG, Guest Car Park Estrada de Baia de N. Senhora da Esperanca"
        if "beijingxueyuanroad" in loc:
            rawadd = "Tesla Center, Xueyuan Road, Beijing"
        if "qingdaoyinchuan" in loc:
            rawadd = "Tesla Center, Yinchuan West Road, Qingdao"
        if "APAC-CN-Tianjin-Wanggang" in loc:
            rawadd = "<MISSING>"
        if "wellington" in loc:
            rawadd = "Wellington 6011"
        if "wenzhoubinhai" in loc:
            rawadd = "Wenzhou Binhai Service Center"
        if "APAC-CN-Wenzhou-Binhai" in loc:
            rawadd = "<MISSING>"
        if "sendaiservice" in loc:
            rawadd = "仙台市宮城野区"
        if "taichungshizhengservice" in loc:
            rawadd = "台中市政服務中心 台中市西屯區市政路638號"
        if "taipeineihuservicecenter" in loc:
            rawadd = "台北市內湖區舊宗路二段1號 賞車或試駕服務請從舊宗路2段1號入口前往"
        if "osakatoyonaka" in loc:
            rawadd = "豊中 大阪府豊中市上津島1丁目1-20"
        if "aichinagoyaservice" in loc:
            rawadd = "名古屋市南区星崎1-41"
        if "tokyobay" in loc:
            rawadd = "東京ベイ 東京都江東区東雲2丁目7-20"
        if "kawasakitomei" in loc:
            rawadd = "東名川崎 神奈川県川崎市宮前区土橋6-10-1"
        if "yokohama" in loc:
            rawadd = "横浜 神奈川県横浜市戸塚区上矢部町995-1"
        if "fukuokaservice" in loc:
            rawadd = "博多市"
        if "gushankaohsiungservice" in loc:
            rawadd = "高雄市鼓山區博愛一路437號"
        if "busanteslacentre" in loc:
            rawadd = "부산광역시 연제구 좌수영로 290"
        if "seoulgangseo" in loc:
            rawadd = "서울특별시 강서구 양천로 66길5"
        if "seoulmunjeong" in loc:
            rawadd = "서울특별시 송파구 동남로4길 36-1"
        if "seoulseungsu" in loc:
            rawadd = "서울특별시 성동구 광나루로 8길 6"
        if "seongnambundang" in loc:
            rawadd = "경기도 성남시 분당구 대왕판교로 316"
        if lat == "" or lng == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "</p>" in hours:
            hours = hours.split("</p>")[0].strip()
        typ = typ.replace("; ", "")
        if typ == "":
            typ = "Store"
        if CS:
            name = name + " - Coming Soon"
        addr = parse_address_intl(rawadd)
        city = addr.city
        zc = addr.postcode
        state = addr.state
        country = addr.country
        add = addr.street_address_1
        if add is None:
            add = "<MISSING>"
        else:
            add = add.strip()
        if state == "" or state is None:
            state = "<MISSING>"
        if state in usstates:
            country = "US"
        if state in castates:
            country = "CA"
        if zc == "" or zc is None:
            zc = "<MISSING>"
        if city == "" or city is None:
            city = "<MISSING>"
        if country == "" or country is None:
            country = "<MISSING>"
        if add == "" or add is None:
            add = "<MISSING>"
        if country == "US":
            try:
                city = locality.split(",")[0].strip()
                state = locality.split(",")[1].strip().split(" ")[0]
                zc = locality.rsplit(" ", 1)[1]
            except:
                pass
        hours = (
            hours.replace(";Mon", "Mon")
            .replace("<br>Mon", "Mon")
            .replace("; Mon", "Mon")
            .replace("<br> Mon", "Mon")
        )
        hours = (
            hours.replace("<br >", "").replace("; Sunday", "Sunday").replace("; ;", ";")
        )
        if city == "" or city is None:
            city = "<MISSING>"
        yield SgRecord(
            locator_domain=website,
            page_url=loc,
            location_name=name,
            raw_address=rawadd,
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
