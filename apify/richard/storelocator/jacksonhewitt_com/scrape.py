from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "Cookie": "visid_incap_410416=sgCDlEvaTbe32jdzQCOnmBUG8GAAAAAAQUIPAAAAAAA0GbsXho3mnUYZg8mrSkJL; trackGuid=A19C3413-87D2-49CC-B7B8-290C55943527; _gcl_au=1.1.479606712.1626344048; initialTrafficSource=utmcsr=(direct)|utmcmd=(none)|utmccn=(not set); ai_user=S8POB|2021-07-15T10:14:08.869Z; nmstat=9432b12f-80ed-e398-7f5e-84a5dbef253d; _pin_unauth=dWlkPVpUYzFZbVk1TmprdFlqYzBNQzAwTjJGaUxXSTNaakl0TWpRMU5EZGlORE14WkRWaQ; _fbp=fb.1.1626344060754.288123387; __qca=P0-23366525-1626344061425; incap_ses_1286_410416=pcF7W0yMbEde/L+kZ8rYEXtU82AAAAAA/I0o0fzA+rT2/dvG6O8WFQ==; ASP.NET_SessionId=jga4gwy0y0dycddp0f02czhb; ARRAffinity=1a80b38a592607dd22e1d5649083b6fbb0ce75e38eeee0509d0e1d467f409704; ARRAffinitySameSite=1a80b38a592607dd22e1d5649083b6fbb0ce75e38eeee0509d0e1d467f409704; nlbi_410416=f8/INvzeKn44YiKiMVdxAAAAAAAzTzCSwJ3KWdtH3SUY4HPv; incap_ses_880_410416=l5E6Cm9gQS0cW6M7sWM2DJxU82AAAAAAuaudt6ZczcamTAa6jjKRaw==; __utmzzses=1; _ga_ZE708DS2MV=GS1.1.1626559649.3.0.1626559649.0; _ga=GA1.2.1680502790.1626344049; _gid=GA1.2.1318745198.1626559651; _uetsid=62787f80e74b11eba678073c22c44b9d; _uetvid=66167f60e55511eb93d44dc195de1d45; is=5ab30e33-80fc-4d41-b545-0411773dfb48; iv=af4a970e-f5c1-437c-9ca7-0d3319202aa3; linkerParam=_ga=2.184015462.1318745198.1626559651-1680502790.1626344049; _gaexp=GAX1.2.gSoq2kJmTAepwCL6DfwZ0g.18893.0; kw_fwABAVu7bX9PmQDE=undefined; _derived_epik=dj0yJnU9Ujg4UkNDUWFPdWdpTmdWZ25Qa0xodXE0VllRS3BYaS0mbj1ScTJ5cFNuSXNZMGQweVV2V19YV1pBJm09MSZ0PUFBQUFBR0R6VktzJnJtPTEmcnQ9QUFBQUFHRHpWS3M; _tq_id.TV-81729009-1.83e6=2a61409598697785.1626344050.0.1626559666..; ai_session=tlVBg|1626559654150.5|1626559917888.3",
    "Host": "www.jacksonhewitt.com",
    "jhafst": "b52ff9b678744f00b511a66753bd290c",
    "Referer": "https://www.jacksonhewitt.com/",
    "Request-Context": "appId=cid-v1:66f283fb-f002-4eef-8768-79c17a1f335a",
    "Request-Id": "|C/HRm.0Dixa",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_data():

    titlelist = []
    zips = static_zipcode_list(radius=30, country_code=SearchableCountries.USA)
    for zip_code in zips:
        url = "https://www.jacksonhewitt.com/api/offices/search/" + zip_code
        try:
            loclist = session.get(url, headers=headers, verify=False).json()["Offices"]
        except:
            continue
        for loc in loclist:

            store = loc["OfficeNumber"]
            lat = loc["Latitude"]
            longt = loc["Longitude"]
            city = loc["City"]
            street = loc["Address1"]
            try:
                street = street + " " + str(loc["Address2"])
            except:
                pass
            try:
                ltype = loc["TypeName"]
                if len(ltype) < 3:
                    ltype = "<MISSING>"
            except:
                ltype = "<MISSING>"
            state = loc["State"]
            pcode = loc["ZipCode"]
            try:
                phone = loc["Phone"].strip()
            except:
                phone = "<MISSING>"
            hourslist = loc["OfficeHours"]
            title = "Hackson Hewitt" + " " + loc["City"]
            link = "https://www.jacksonhewitt.com/" + loc["DetailsUrl"]
            hours = ""
            for hr in hourslist:
                hours = hours + hr["DayOfWeek"] + " " + hr["Hours"] + " "
            if link in titlelist:
                continue
            titlelist.append(link)

            yield SgRecord(
                locator_domain="https://www.jacksonhewitt.com/",
                page_url=link,
                location_name=title,
                street_address=street.replace(" None", "").strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=store,
                phone=phone,
                location_type=ltype,
                latitude=lat,
                longitude=longt,
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
