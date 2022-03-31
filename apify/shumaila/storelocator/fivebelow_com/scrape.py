from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


headers = {
    "authority": "locations.fivebelow.com",
    "method": "GET",
    "path": "/index.html?q=35007&qp=35007&l=en",
    "scheme": "https",
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "visid_incap_881946=U4fgrBwNSpuUDhYu0htB2OMRlmEAAAAAQUIPAAAAAADbMFsJ03rdaRVPkoxhNg1C; _pxvid=6da82303-484b-11ec-8e33-5a7259625851; visid_incap_2317415=CvkRlAp9RMmmnx0MByUGaeYRlmEAAAAAQUIPAAAAAABhnWNuiCZQqSWH55UKxWOt; _ga=GA1.2.2053820546.1637224936; _gid=GA1.2.467865139.1637224936; _gcl_au=1.1.1439298613.1637224936; _gaexp=GAX1.2.d33XqL4PQoaV6VhbA-5_RQ.19040.1; _scid=8dd22417-c37d-47fe-bf9b-ec0e6aa10fd9; _mkto_trk=id:116-SSG-817&token:_mch-fivebelow.com-1637224939724-61582; _fbp=fb.1.1637224940013.588912163; _pin_unauth=dWlkPVpUYzFZbVk1TmprdFlqYzBNQzAwTjJGaUxXSTNaakl0TWpRMU5EZGlORE14WkRWaQ; _sctr=1|1637175600000; _hjSessionUser_813165=eyJpZCI6IjZlYjliYmQwLWUxNTgtNWYwZC05OGVhLTliMzQzOGI1MGIyNSIsImNyZWF0ZWQiOjE2MzcyMjQ5NDAxMjQsImV4aXN0aW5nIjp0cnVlfQ==; _ga=GA1.3.2053820546.1637224936; _gid=GA1.3.467865139.1637224936; _pin_unauth=dWlkPVpUYzFZbVk1TmprdFlqYzBNQzAwTjJGaUxXSTNaakl0TWpRMU5EZGlORE14WkRWaQ; _yfpc=1494153159981; nlbi_881946=6Fqlen/ggx6XnQeanuWV7gAAAACkuhDWm8z3jkzrimCfaY2c; incap_ses_963_881946=z7A0N6YmBgRQTMD310NdDbuFlmEAAAAALYMy2Xks0mPFe8/wcogG6A==; pxcts=79f395e1-4890-11ec-b34d-a7df8a7ae788; _px3=619ff20a4a1a83a3dcaf5205212646693acf49d5e49649d1154d44b7df6810aa:zRIHdWYimbfBGFqhvR26hRFI/uWv8m/VLrqPeMql/1I2aAMXJlzbz6mOzg+RIxiGwWNKCMtFh9dUzN33HOk+2A==:1000:p178UYWiuGlqNdckrB20iIXwjP58X4HHqK5TSuqaMHXmN6DgyNcKlAIRJr9JiUVB0P2VJmnnDKkXsVS5wjPS6iYKyWRPHttSe/fX6+YujfsA6duJeULzF+pgl+sMnMnMcCdfW00960w/8eq/0I81Tu7rUSbsGOMMBal7NPs3qDIAZdNSNJ/v+ZhK/eE7CwjXiLnHzeUnutBQwvvFxPASjg==; nlbi_881946_2147483646=gUajMfqnIFxfeapxnuWV7gAAAABeq0r0XZQ1uqNWp0QSmAGO; incap_ses_963_2317415=YWCbKRr9xicbU8D310NdDcCFlmEAAAAAPHVP16akbcJbdZqZWbAeDA==; _gat=1; _dc_gtm_UA-169953857-1=1; SnapABugRef=https%3A%2F%2Fwww.fivebelow.com%2F%20; SnapABugHistory=2#; _hjSession_813165=eyJpZCI6IjI5OGUyNDc4LWJlZjktNGE4Mi1iOWM2LTZjNWY4ZmYzNGVkOSIsImNyZWF0ZWQiOjE2MzcyNTQ1OTY1NDF9; _hjAbsoluteSessionInProgress=1; _derived_epik=dj0yJnU9S0VsMVAwaFFOUk5PVkw3QXNSQ3hpc2ZTZ1ZfMHZuWmEmbj0yYnRJMDF3VFFaejJMd2VPdE01R3FBJm09MSZ0PUFBQUFBR0dXaGN3JnJtPTEmcnQ9QUFBQUFHR1doY3c; __cf_bm=BMYgZg7neoUF2Dsz98QLOmGfj.ovFLnQqM7uaNr2ln8-1637254609-0-AfkrKAvcBDrsq35gh5jlTZflBtUixBg4qabbVIoB0A7MBA/+XgzHPbYpWVVf/3EZlfxCUJgn/DFkD0sxPD9cFMM=; _gat_client=1; _gat_yext=1; SnapABugUserAlias=%23; SnapABugVisit=4#1637254596; _uetsid=704454f0484b11ec9e6de1de7bfd3f12; _uetvid=70447180484b11ec99774390eee593c5; _derived_epik=dj0yJnU9VHpVQ1FWX1BSRklFLV9TTDhCcXctV09PTVdBcFJzMEQmbj1fX3VVWmVBT3V0aWR5WkdWc2hXRGhnJm09MSZ0PUFBQUFBR0dXaGRRJnJtPTEmcnQ9QUFBQUFHR1doZFE; _gali=search-form",
    "referer": "https://locations.fivebelow.com/",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    session = SgRequests()
    mylist = static_zipcode_list(radius=10, country_code=SearchableCountries.USA)
    for zip_code in mylist:

        url = (
            "https://locations.fivebelow.com/index.html?q="
            + str(zip_code)
            + "&qp="
            + str(zip_code)
            + "&l=en"
        )
        try:
            headers["path"] = url.replace("https://locations.fivebelow.com", "")
            loclist = session.get(url, headers=headers).json()["response"]["entities"]
        except:
            try:
                session = SgRequests()
                headers["path"] = url.replace("https://locations.fivebelow.com", "")
                loclist = session.get(url, headers=headers).json()["response"][
                    "entities"
                ]
            except:
                continue
        for loc in loclist:
            loc = loc["profile"]

            city = loc["address"]["city"]
            state = loc["address"]["region"]
            ccode = loc["address"]["countryCode"]
            pcode = loc["address"]["postalCode"]
            street = (
                loc["address"]["line1"]
                + " "
                + str(loc["address"]["line2"])
                + " "
                + str(loc["address"]["line3"])
            )
            street = street.replace("None", "")
            link = loc["c_pagesURL"]

            try:
                lat = loc["geocodedCoordinate"]["lat"]
                longt = loc["geocodedCoordinate"]["long"]
            except:
                lat = loc["yextDisplayCoordinate"]["lat"]
                longt = loc["yextDisplayCoordinate"]["long"]
            try:
                phone = loc["mainPhone"]["display"]
            except:
                phone = "<MISSING>"
            try:
                store = loc["facebookStoreId"]
            except:
                store = "<MISSING>"
            link = loc["c_pagesURL"]
            title = loc["c_aboutSectionTitle"]
            hours = ""
            try:
                hourslist = loc["hours"]["normalHours"]
                for hr in hourslist:

                    day = hr["day"]

                    if str(hr["isClosed"]) != "False":

                        hours = hours + day + " " + " Closed "
                    else:

                        start = (
                            str(hr["intervals"][0]["start"])[0:2]
                            + ":"
                            + str(hr["intervals"][0]["start"])[2:]
                            + " am "
                        )
                        endd = int(str(hr["intervals"][0]["end"])[0:2])
                        if endd > 12:
                            endd = endd - 12
                        endstr = (
                            str(endd)
                            + ":"
                            + str(hr["intervals"][0]["end"])[2:]
                            + " pm "
                        )

                        hours = hours + day + " " + start + " - " + endstr
            except:

                hours = "<MISSING>"
            if len(hours) < 3:
                hours = "<MISSING>"
            yield SgRecord(
                locator_domain="https://fivebelow.com/",
                page_url=link,
                location_name=title.replace("five below ", "").strip(),
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=str(store),
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
            )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
