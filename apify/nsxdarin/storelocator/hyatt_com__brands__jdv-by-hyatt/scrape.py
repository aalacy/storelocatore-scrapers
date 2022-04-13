from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "cookie": "vrid=rBEAAmHUtmQJIwAO86wnAg==; s_ecid=MCMID%7C35479009558481717750971710220968154631; rand_1to3=2; rndn=36; email_90_10=test; _fbp=fb.1.1641330270676.102027258; _ga=GA1.2.510791273.1641330271; mdLogger=false; cd_user_id=17e26e86566197-082f917b7bab82-4303066-1fa400-17e26e86568963; kampyleUserSession=1641920696638; kampyleUserSessionsCount=33; kampyleSessionPageCounter=1; source-country=US; mb_locale=en-US; check=true; AMCVS_D7B27FF452128BAA0A490D4C%40AdobeOrg=1; OptanonConsent=isIABGlobal=false&datestamp=Fri+Apr+01+2022+09%3A59%3A36+GMT-0500+(Central+Daylight+Time)&version=6.30.0&hosts=&consentId=f36ff1ba-1c89-46f2-aba2-ef454a40ca80&interactionCount=1&landingPath=NotLandingPage&groups=BG8%3A1%2CC0004%3A1%2CC0005%3A1%2CC0003%3A1%2CC0002%3A1%2CC0001%3A1&AwaitingReconsent=false; fs_sampling=s; newvisit=true; scPrevPage=Global:explore-hotels; s_p26=en-US; c_m=Typed%2FBookmarkedTyped%2FBookmarkedundefined; s_cmch=%5B%5B%27typed%2Fbookmarked%27%2C%271648825176862%27%5D%5D; s_cmkw=%5B%5B%27n%2Fa%27%2C%271648825176862%27%5D%5D; s_advcs=%5B%5B%27typed%2Fbookmarked%27%2C%271648825176864%27%5D%5D; s_cc=true; AMCV_D7B27FF452128BAA0A490D4C%40AdobeOrg=-330454231%7CMCIDTS%7C19084%7CMCMID%7C35479009558481717750971710220968154631%7CMCAAMLH-1649429976%7C9%7CMCAAMB-1649429976%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1648832375s%7CNONE%7CMCAID%7CNONE%7CMCCIDH%7C-736669958%7CvVersion%7C3.1.2; utag_main=v_id:017e26e85fac0020ba64311d859005073005606b00bd0$_sn:4$_ss:1$_st:1648826976767$_ga:017e26e85fac0020ba64311d859005073005606b00bd0$vapi_domain:hyatt.com$dc_visit:4$_pn:1%3Bexp-session$ses_id:1648825176767%3Bexp-session$dc_event:1%3Bexp-session; _cs_c=0; _cs_id=cacf0e60-528e-aeb5-a8c5-752320991c79.1648825177.1.1648825177.1648825177.1.1682989177112; AAMC_hyatt_0=REGION%7C9%7CAMSYNCSOP%7C%7CAMSYNCS%7C; aam_uuid=40887640205789290210359915672558665605; tkrm_alpekz_s1.3-ssn=0IjQ1P5XeqSzSnO7gq5yOUcq4JUux5ExGMjlPqVAemNE5UQX7lKMy3jfzKxp6icT1Gb4Uc7ZhihknDr5xfhx1AIueQJwhoMPDoTffrOVGmjbmtAV5efblIVipwIjK21rnXwBRRfY5yrRzmffFiD34b2Az; tkrm_alpekz_s1.3=0IjQ1P5XeqSzSnO7gq5yOUcq4JUux5ExGMjlPqVAemNE5UQX7lKMy3jfzKxp6icT1Gb4Uc7ZhihknDr5xfhx1AIueQJwhoMPDoTffrOVGmjbmtAV5efblIVipwIjK21rnXwBRRfY5yrRzmffFiD34b2Az",
}

logger = SgLogSetup().get_logger("hyatt_com__brands__jdv-by-hyatt")


def fetch_data():
    url = "https://www.hyatt.com/explore-hotels/service/hotels"
    r = session.get(url, headers=headers)
    logger.info(f"Response: {r}")
    website = "hyatt.com/brands/jdv-by-hyatt"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '{"spiritCode":"' in line:
            items = line.split('"spiritCode":"')
            for item in items:
                if '"brand":{"key":"' in item:
                    phone = "<MISSING>"
                    CS = False
                    name = item.split('"name":"')[1].split('"')[0]
                    loc = (
                        "https://www.hyatt.com"
                        + item.split('"url":"https://www.hyatt.com')[1].split('"')[0]
                    )
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split("}")[0]
                    hours = "<MISSING>"
                    typ = (
                        item.split('"brand":{"key":"')[1]
                        .split('"label":"')[1]
                        .split('"')[0]
                    )
                    store = item.split('"')[0]
                    country = item.split('"country":{"key":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    zc = item.split('"zipcode":"')[1].split('"')[0]
                    add = item.split('"addressLine1":"')[1].split('"')[0]
                    try:
                        add = (
                            add + " " + item.split('"addressLine2":"')[1].split('"')[0]
                        )
                    except:
                        pass
                    try:
                        state = item.split('"stateProvince":{"key":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    zc = item.split('"zipcode":"')[1].split('"')[0]
                    if loc == "":
                        loc = "<MISSING>"
                    if zc == "":
                        zc = "<MISSING>"
                    if typ == "":
                        typ = "<MISSING>"
                    logger.info(loc)
                    try:
                        r2 = session.get(loc, headers=headers)
                        for line2 in r2.iter_lines():
                            if ">Coming " in line2:
                                CS = True
                            if ">Opening " in line2:
                                CS = True
                            if '"telephone":"' in line2:
                                phone = line2.split('"telephone":"')[1].split('"')[0]
                    except:
                        pass
                    if "wasxs" in loc:
                        CS = False
                    if "Club Maui, " in name:
                        name = "Hyatt Residence Club Maui, Kaanapali Beach"
                    if CS:
                        hours = "Coming Soon"
                    if "dxbzm" in loc:
                        hours = "<MISSING>"
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
