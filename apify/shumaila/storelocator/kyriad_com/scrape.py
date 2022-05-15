import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "cookie": "currency=GBP; locale=en-us; bm_mi=95958D485FFFC41A11A40627CFA982D0~sCwcqs9ImuHoddcbTqTrIwfyNGEiAIxWfDZs3Umwx5HqcMc+6JlT1mhG3Bk0INmSPXp+8FyW3EvEfIf85scoRNIwgjuHkjbNeqUkeoVaCSFYgE3fGSIbzTu+pXoSpuh5X/kzTjzD2mJTyrf9XRjkubv/LldWfcfi2ixL4igBbLbw93lia2oX1EkvOYWsOjNulG03ZOJEyFB512U2VF2dX8w9ku3a6p+EkXXxJotYrUh9y3h/xKv0Sk2rjk7qtzcAEHPLsGSgmQyYWi8opRDAcQ==; ak_bmsc=6EDE941170464B926AB0E9A319DFAA31~000000000000000000000000000000~YAAQXwPUF+qA2FJ/AQAA7ObHkw/E1lLvah9C/7gAVzAOGDG5h29SMCI6Z6GJ45/X4Ak7V6MQGPu3PpMoMxIXDaJMrbyj14LO57Czj3EU61gYyyQdBpWC/ycHsjojfUd4xvZTvQGCV3nR8H2v8k8vJUSnBasN+IhLTA3bc+MJj23QqTGKHL2p/iT5P556ItaMmo+BgNstjdX4OEyMeMpowedOC+D3dwlzKPy3Eoy4LmkZx0b3wa8114dGAA0oTTGaqRQ+0z8uGL/B2upAInkTc/DsUhSeb/82dXf3YwDq2A6Zc1uzyD41ZvRj0uE3cz0hr6f9ENOiR6kNrnsArPqDHYf/iMJwpaFwsIcJnt9a4n94n2nwjG7F/haDFYo3u2JL6SwEpQREsK/NBLaTR5j3QsBrjh3zp79NskPJMe3OMCycs+eK; OptanonAlertBoxClosed=2022-03-16T17:30:56.982Z; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Mar+16+2022+22%3A30%3A56+GMT%2B0500+(Pakistan+Standard+Time)&version=6.31.0&isIABGlobal=false&hosts=&consentId=8d9a51a6-0184-423c-9446-fb5d267090a8&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false; kameleoonVisitorCode=_js_6rrhknrmlm7fw3df; _ga=GA1.2.482308551.1647451858; _gid=GA1.2.1543188146.1647451858; _gat_UA-52847020-12=1; _cs_c=0; _uetsid=d802e2d0a54e11ec8a40d39f7601127c; _uetvid=d8030d40a54e11ec962cb9ed7a5786ad; _gcl_au=1.1.2128136778.1647451860; bm_sv=A426E0E35584B00DC31D0847B17C8B4F~2W+C2k/Xas0Iu5iwpa03iDnUOIcgapoliC8MGcQvBnryR341ddlcCOBzc5hGf5kHuTU7kFM5eCf6DjkB91o2Nw0Qxm7OAVjHCS690Viq4CCroFhxy4UXSKIiFIAl8OZYKorAby3ZVfH7lNAq5JqEWqUj/AhTswRCagBM+C7KTCQ=; _fbp=fb.1.1647451861974.336478271; _clck=127d2z4|1|ezt|0; _clsk=1bu8z4n|1647451863358|1|1|k.clarity.ms/collect; _cs_id=6df07ced-d34e-a761-eecc-115b8024900d.1647451858.1.1647451883.1647451858.1.1681615858875; _cs_s=2.5.0.1647453683381",
    "origin": "https://www.kyriad.com",
}

headers1 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    apiurl = "https://api.kyriad.com/api/v1/graphql"
    url = "https://www.kyriad.com/en-us/our-hotels"
    r = session.get(url, headers=headers1)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.select("a[href*=our-hotels]")

    linklist = []
    for state in statelist:
        try:
            term = state.find("h2").text
        except:
            continue
        if "Hotels " in state.text:
            continue
        dataobj = (
            '{"operationName":"resortsSearchQueryV2","variables":{"resortsSearchInput":{"homePageUrl":"https://www.kyriad.com","term":"'
            + term
            + '","searchBy":"OLD_REGION","code":"","locale":"en-us","brandCode":"KY","withRandomOrder":true,"withCrossSell":false,"top":null}},"query":"query resortsSearchQueryV2($resortsSearchInput: MbResortsSearchInputType!) {\n  resortsSearchV2(resortsSearchInput: $resortsSearchInput) {\n    crossSellBrandResorts {\n      ...ResortFavorite\n      ...ResortSearchData\n      __typename\n    }\n    currentBrandResorts {\n      ...ResortFavorite\n      ...ResortSearchData\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ResortFavorite on MbResortType {\n  id: resortCode\n  isFavorite\n  __typename\n}\n\nfragment ResortSearchData on MbResortType {\n  resortCode\n  resortName\n  brandCode\n  city\n  cityPageUrl\n  mainPicture\n  stars\n  distanceFromDownTown\n  website\n  brandMapIconUrl\n  brandMapIconAlt\n  tripAdvisorRating\n  tripAdvisorRatingImageUrl\n  tripAdvisorNbReviews\n  isRenovated\n  isOldWebsite\n  location {\n    longitude\n    latitude\n    __typename\n  }\n  preferredLocales {\n    isDefault\n    localeCode\n    __typename\n  }\n  eReputation {\n    score\n    reviewsCount\n    scoreDescription\n    __typename\n  }\n  externalBookingEngineUrl\n  isCutOffOutDated\n  __typename\n}\n"}'
        )
        try:
            loclist = session.post(apiurl, data=dataobj, headers=headers).json()[
                "data"
            ]["resortsSearchV2"]["currentBrandResorts"]
        except:
            continue
        for loc in loclist:

            link = loc["website"]
            if link in linklist:
                continue
            linklist.append(link)

            store = loc["id"]
            try:
                session1 = SgRequests()
                r = session1.get(link, headers=headers1)
            except:
                continue
            try:
                content = r.text.split('<script type="application/ld+json">', 1)[
                    1
                ].split("</script", 1)[0]

                content = (json.loads(content))["mainEntity"][0]["mainEntity"]
            except:
                continue
            title = content["name"]

            street = content["address"]["streetAddress"].replace("\n", " ").strip()
            city = content["address"]["addressLocality"]
            pcode = content["address"]["postalCode"]
            ccode = content["address"]["addressCountry"]
            phone = content["telephone"]
            lat, longt = content["hasMap"].split("=")[-1].split(",")
            hours = str(content["checkinTime"]) + " - " + str(content["checkoutTime"])

            yield SgRecord(
                locator_domain="https://www.kyriad.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=SgRecord.MISSING,
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=str(store),
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
