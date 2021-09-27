from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "cookie": "COOKIE_ANONYMUS_USER_ID=3a8aacd5-d2b2-4696-868d-12994c2ac275; visid_incap_2222787=9nvu9RJESGmbn9JeRxZ7e1bhUWEAAAAAQUIPAAAAAACtTD2yE8kPD3f0W8qW/Lk7; nlbi_2222787=xnIiQqquGREJhqQF2AINKgAAAABy/4A4rpHq11T/aoSoDGjv; incap_ses_1426_2222787=6Z9odLFwuDYUppsykCvKE1fhUWEAAAAA9pyvQiAdCraE20aO4gU7oA==; __RequestVerificationToken=BtUjBV0hk4XUrP_pzcLo4WRR4VRZzsUEUQxZqrUZr_yv9ACaaltZoUcQfqYbTzfGrFgnXfDYXJsaCcdR19T_9dJ04K41; COOKIE_CURRENT_PAGE=%2f; COOKIE_IS_PRIVATE=False; _pk_id.3.e73a=797c1f2f48871cd6.1632756048.; _pk_ses.3.e73a=1; _gcl_au=1.1.2080818486.1632756048; IsClearCartEcom=true; _gid=GA1.2.1962789935.1632756049; _gat_UA-23943946-10=1; _gat_UA-133195892-1=1; _fbp=fb.1.1632756049277.1624814118; __hstc=255627863.e09cafd994d077dcf184866b6040aa07.1632756050238.1632756050238.1632756050238.1; hubspotutk=e09cafd994d077dcf184866b6040aa07; __hssrc=1; COOKIE_SESSION_ID=797c1f2f48871cd6; COOKIE_CURRENT_PAGE_URL=https://www.unitedsupermarkets.com/rs/StoreLocator; reese84=3:I5jQuH1MFynRDECc+dObzA==:F31AxEQZ77dBW/7WHoRGo0Ck4XQzDgL9KJkYd8Eq9wgQubcUJxLpadG4Y5TrcTts/MxwEmTR51gyymIZdTMHtXXSoT/6LM4M5Rc6Xk1UT5j4FQ2W+I1ibWoZrQOUL1kSK7Cgk/3RfysyjE5ATiPLuYNWPiZZum7HbV8biSX151QkiMTGDxAiAld60Io3fD7RYuaUX2bDFiVmGgvAMyM88XQh+T3PPeihxRRkcmAaBMLInI9qd6j4o4BjmZBogV0z4D3G/t5wRitvZ9MK59vRcvgAX1DzSlRyW4XDTExOJ0pRiu2jCOsromQc2D7NP9aAsCHdhgHzsMKR9nBTDf04GKabF6Xi+t7S2RlgrnR9DHnHejwdhVyaa7zqBz/12nQHezYhKOHsRVROadLDjck0blHGMzUsr5Vuh1l2fxuRiYepJU0v6bkIqBsY8r3piLHP:Y04T4LXpiARgQbIQaJ3xER+fHNo0YLGhy66WRHGAaSA=; _ga=GA1.1.168075462.1632756048; __hssc=255627863.2.1632756050239; _ga_NPJPL39KQ6=GS1.1.1632756047.1.1.1632756079.0; _ga_JY5T7ZBHQ4=GS1.1.1632756047.1.1.1632756079.0; _ga_3SPK8GPCTJ=GS1.1.1632756049.1.1.1632756079.0; BE_CLA3=p_id%3D2P4L6A4NL8P4RNL6JLPNJ8RR8AAAAAAAAH%26bf%3D55eef48d91c2cc4e630f99887fddcba9%26bn%3D3%26bv%3D3.43%26s_expire%3D1632842479862%26s_id%3D2P4L6A4NL8P4R6A2NNNNJ8RR8AAAAAAAAH; nlbi_2222787_2147483646=Vq0RUcXLI1acp/gx2AINKgAAAACu3LZBMkI0QIByE7oyUvdZ",
}

logger = SgLogSetup().get_logger("unitedsupermarkets_com")


def fetch_data():
    url = "https://www.unitedsupermarkets.com/RS.Relationshop/StoreLocation/GetListClosestStores"
    r = session.get(url, headers=headers)
    website = "unitedsupermarkets.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"Distance":' in line:
            items = line.split('{"Distance":')
            for item in items:
                if '"Logo":"' in item:
                    name = item.split('"StoreName":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    add = item.split('"Address1":"')[1].split('"')[0]
                    store = item.split('"StoreID":')[1].split(",")[0]
                    loc = (
                        "https://www.unitedsupermarkets.com/rs/StoreLocator?id=" + store
                    )
                    state = item.split('"State":"')[1].split('"')[0]
                    zc = item.split('"Zipcode":"')[1].split('"')[0]
                    phone = item.split('"PhoneNumber":"')[1].split('"')[0]
                    lat = item.split('"Latitude":')[1].split(",")[0]
                    lng = item.split('"Longitude":')[1].split(",")[0]
                    hours = item.split('"StoreHours":"')[1].split('"')[0]
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
