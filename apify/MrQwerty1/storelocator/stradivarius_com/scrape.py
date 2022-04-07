from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    apis = [
        "https://www.stradivarius.com/itxrest/2/bam/store/54109556/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=51.5072178&longitude=-0.1275862&min=100&receiveEcommerce=false&countryCode=GB&languageId=-1&radioMax=50000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009585/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=42.506287&longitude=1.521801&receiveEcommerce=false&countryCode=AD&languageId=-13&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009581/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=23.424076&longitude=53.847816&receiveEcommerce=false&countryCode=AE&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009638/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=41.15333&longitude=20.168331&receiveEcommerce=false&countryCode=AL&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009630/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=40.0691&longitude=45.03819&receiveEcommerce=false&countryCode=AM&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009626/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=40.143105&longitude=47.576927&receiveEcommerce=false&countryCode=AZ&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/54009552/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=50.503887&longitude=4.469936&receiveEcommerce=false&countryCode=BE&languageId=100&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009593/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=42.733883&longitude=25.48583&receiveEcommerce=false&countryCode=BG&languageId=-30&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009587/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=26.0667&longitude=50.5577&receiveEcommerce=false&countryCode=BH&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009615/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=4.570868&longitude=-74.29733&receiveEcommerce=false&countryCode=CO&languageId=-48&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009622/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=9.934739&longitude=-84.087502&receiveEcommerce=false&countryCode=CR&languageId=-5&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009584/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=35.12641&longitude=33.42986&receiveEcommerce=false&countryCode=CY&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009609/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=49.817493&longitude=15.472962&receiveEcommerce=false&countryCode=CZ&languageId=-27&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009617/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=18.735693&longitude=-70.16265&receiveEcommerce=false&countryCode=DO&languageId=-5&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009639/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=28.033886&longitude=1.659626&receiveEcommerce=false&countryCode=DZ&languageId=-2&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009624/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=-1.831239&longitude=-78.1834&receiveEcommerce=false&countryCode=EC&languageId=-5&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009597/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=58.595272&longitude=25.013607&receiveEcommerce=false&countryCode=EE&languageId=-34&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009592/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=26.820553&longitude=30.802498&receiveEcommerce=false&countryCode=EG&languageId=-44&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/54009550/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=40.46367&longitude=-3.74922&receiveEcommerce=false&countryCode=ES&languageId=-5&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/54009551/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=46.22764&longitude=2.213749&receiveEcommerce=false&countryCode=FR&languageId=-2&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009623/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=42.315407&longitude=43.35689&receiveEcommerce=false&countryCode=GE&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009559/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=39.074207&longitude=21.824312&receiveEcommerce=false&countryCode=GR&languageId=-14&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009598/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=15.783471&longitude=-90.23076&receiveEcommerce=false&countryCode=GT&languageId=-5&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009634/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=15.199999&longitude=-86.241905&receiveEcommerce=false&countryCode=HN&languageId=-5&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009575/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=45.1&longitude=15.2&receiveEcommerce=false&countryCode=HR&languageId=-38&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009600/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=47.162495&longitude=19.503304&receiveEcommerce=false&countryCode=HU&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009601/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=-0.789275&longitude=113.921326&receiveEcommerce=false&countryCode=ID&languageId=-49&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009557/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=53.41291&longitude=-8.24389&receiveEcommerce=false&countryCode=IE&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009602/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=31.046051&longitude=34.851612&receiveEcommerce=false&countryCode=IL&languageId=-52&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/54009555/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=41.87194&longitude=12.56738&receiveEcommerce=false&countryCode=IT&languageId=-4&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009588/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=30.585163&longitude=36.238415&receiveEcommerce=false&countryCode=JO&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009582/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=29.31166&longitude=47.481766&receiveEcommerce=false&countryCode=KW&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009603/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=48.019573&longitude=66.92368&receiveEcommerce=false&countryCode=KZ&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009583/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=33.85472&longitude=35.862286&receiveEcommerce=false&countryCode=LB&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009605/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=55.169437&longitude=23.881275&receiveEcommerce=false&countryCode=LT&languageId=-33&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/54009561/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=49.815273&longitude=6.129583&receiveEcommerce=false&countryCode=LU&languageId=-2&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009604/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=56.879635&longitude=24.60319&receiveEcommerce=false&countryCode=LV&languageId=-35&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009586/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=31.791702&longitude=-7.09262&receiveEcommerce=false&countryCode=MA&languageId=-2&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009608/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=42.70868&longitude=19.37439&receiveEcommerce=false&countryCode=ME&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009629/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=41.608635&longitude=21.745275&receiveEcommerce=false&countryCode=MK&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009589/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=35.937496&longitude=14.375416&receiveEcommerce=false&countryCode=MT&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009570/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=23.6345&longitude=-102.55279&receiveEcommerce=false&countryCode=MX&languageId=-50&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009982/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=12.865416&longitude=-85.20723&receiveEcommerce=false&countryCode=NI&languageId=-5&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/54009553/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=52.132633&longitude=5.291266&receiveEcommerce=false&countryCode=NL&languageId=100&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009591/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=21.473534&longitude=55.975414&receiveEcommerce=false&countryCode=OM&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009633/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=8.537981&longitude=-80.78213&receiveEcommerce=false&countryCode=PA&languageId=-5&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009621/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=12.879721&longitude=121.77402&receiveEcommerce=false&countryCode=PH&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/54009574/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=51.919437&longitude=19.145136&receiveEcommerce=false&countryCode=PL&languageId=-22&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/54009560/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=39.39987&longitude=-8.224454&receiveEcommerce=false&countryCode=PT&languageId=-6&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009590/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=25.354826&longitude=51.183884&receiveEcommerce=false&countryCode=QA&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009573/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=45.94316&longitude=24.96676&receiveEcommerce=false&countryCode=RO&languageId=-21&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009610/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=44.01652&longitude=21.00586&receiveEcommerce=false&countryCode=RS&languageId=-53&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009572/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=61.52401&longitude=105.318756&receiveEcommerce=false&countryCode=RU&languageId=-20&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009580/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=23.885942&longitude=45.079163&receiveEcommerce=false&countryCode=SA&languageId=-44&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009596/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=46.15124&longitude=14.995463&receiveEcommerce=false&countryCode=SI&languageId=-36&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009595/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=48.669025&longitude=19.699024&receiveEcommerce=false&countryCode=SK&languageId=-28&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009594/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=13.794185&longitude=-88.89653&receiveEcommerce=false&countryCode=SV&languageId=-5&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009637/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=33.886917&longitude=9.537499&receiveEcommerce=false&countryCode=TN&languageId=-2&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/54009571/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=38.963745&longitude=35.24332&receiveEcommerce=false&countryCode=TR&languageId=-43&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009613/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=48.379433&longitude=31.16558&receiveEcommerce=false&countryCode=UA&languageId=-47&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009625/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=43.915886&longitude=17.679075&receiveEcommerce=false&countryCode=BA&languageId=-1&radioMax=5000&appId=1",
        "https://www.stradivarius.com/itxrest/2/bam/store/55009645/physical-store?favouriteStores=true&lastStores=false&closerStores=true&latitude=42.602634&longitude=20.902977&receiveEcommerce=false&countryCode=XK&languageId=-1&radioMax=5000&appId=1",
    ]

    for api in apis:
        cc = api.split("Code=")[1].split("&")[0]
        locator_domain = f"https://www.stradivarius.com/{cc.lower()}"
        r = session.get(api, headers=headers)
        js = r.json()["closerStores"]

        for j in js:
            street_address = ", ".join(j.get("addressLines") or [])
            city = j.get("city") or ""
            state = j.get("state")
            postal = j.get("zipCode") or ""
            if str(postal) == "0":
                postal = SgRecord.MISSING
            store_number = j.get("id")
            location_name = j.get("name")
            page_url = f"https://www.stradivarius.com/{cc.lower()}/store-locator/{city.lower()}/-s{store_number}.html"
            try:
                phone = j["phones"][0]
            except:
                phone = SgRecord.MISSING
            if phone.strip() == "-":
                phone = SgRecord.MISSING
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            _tmp = []
            days = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            try:
                hours = j["openingHours"]["schedule"]
            except:
                hours = []

            for h in hours:
                weekdays = h.get("weekdays") or []
                inters = h.get("timeStripList") or []
                _inters = []
                for i in inters:
                    start = i.get("initHour")
                    end = i.get("endHour")
                    _inters.append(f"{start}-{end}")

                inter = "|".join(_inters)
                for w in weekdays:
                    day = days[int(w) - 1]
                    _tmp.append(f"{day}: {inter}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=cc,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
