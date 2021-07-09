import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "Host": "www.cubesmart.com",
    "Origin": "https://www.cubesmart.com",
    "Referer": "https://www.cubesmart.com/storage-locations",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

cookielist = [
    "_ga=GA1.2.1605234886.1620488575; _gcl_au=1.1.918372723.1620488576; aam_uuid_opt=06256971139219621033527052771413870466; _fbp=fb.1.1620488889828.1871037673; _pin_unauth=dWlkPVpUYzFZbVk1TmprdFlqYzBNQzAwTjJGaUxXSTNaakl0TWpRMU5EZGlORE14WkRWaQ; _st_bid=0939cf00-93d6-11eb-bc89-0f12746e63bb; _usiTracking=4064102; aam_test=aam%3D3684620; LPVID=NiZDFkNDM3MWZjYTc4ZjBj; visid_incap_2413170=UYWZywgMT9G57YsgP8C2+bOwlmAAAAAAQ0IPAAAAAACAd4ucAS0rDlZpxsTZ82QF9tfjVvE9tKLY; nlbi_2413170=m8eKVSbW9gsCoFy2/cPt3AAAAADR74Bhx+Ucmfsn4xBiqBpV; incap_ses_207_2413170=Mjn2cjJ5ymVnWIFxxGnfAiUnv2AAAAAAPOBPCSYbY58u8tWM28NJhA==; at_check=true; _gid=GA1.2.1342296470.1623140139; mboxEdgeCluster=38; AMCVS_FA78F19C55BA9FAA7F000101%40AdobeOrg=1; ASP.NET_SessionId=3tdskz1mfjqka5bksiuds2rn; s_cc=true; incap_ses_530_2413170=MlUdUTdBuTBYWuzvmfBaB5Asv2AAAAAAKuu5Z49I82m1DSDsuUElxQ==; search_term=; s_plt=%5B%5BB%5D%5D; s_pltp=%5B%5BB%5D%5D; AMCV_FA78F19C55BA9FAA7F000101%40AdobeOrg=-637568504%7CMCIDTS%7C18787%7CMCMID%7C06220023048075832883530184630691412429%7CMCAAMLH-1623746763%7C7%7CMCAAMB-1623746763%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1623149163s%7CNONE%7CvVersion%7C5.1.1%7CMCAID%7CNONE; s_sq=%5B%5BB%5D%5D; LPSID-22469663=MYs3IRP-S4-VNZM7yoCaTw; _ce.s=v11.rlc~1623142541578~v11slnt~1623141535561; gpv_pageName=no%20value; mbox=PC#ecd6e123c41646ee84167cc509812e27.38_0#1686387356|session#0bd6512fa8674eeba4afa608d5a1b409#1623144394; _uetsid=b9a12b80c83111eb960a53c56458616a; _uetvid=13679d00b01411eb8b98e188bf556b85; reese84=3:60TANpQknpoKfxsUXeEJ9Q==:ri3POIlmoGHQCqlbsIVetzebWK4pA1z3HErUUWGkkmZEngLvbbMtKt4oMQImqELf879nrMjs0ik13AiTm0cDZZ4LM8kio325G45Ne8rcyKUHNq59Oh92BKxuYLJDPkUFEpECs7settbBdEosq0Q+LyxREVl1wyl3hdj8GYrlx/9UhFWg9H+O6+ajScWfieCs2xBimyEvva5SZ1c9NvkIGJdNZ7vvSZxbPs+6wrtvrDHUGXfntymrcExvEfK5T+6RBgAdzTKwTdFFYYZoTCFUdjSCCJny0343XeeyGqVU+Gbe/5IZ1GBfc6uCKsgzSWYbmw3urtE85zwKcL6T6NDtxvmig7rzrrodx2dXdz0P3JD4Jc+zg+y3ZLVGIf7XGB/6rv65TrvUroHFrvYoV3HDoFmDgyI9DZl76ETGTxVJqsc=:8hQm7GO42Lb6iJAT6zo+myojmqL4qaI7M3n2us3hmwg=; _st=0939cf00-93d6-11eb-bc89-0f12746e63bb.c1513710-c831-11eb-8a62-a95a6f722872.8555802831.(855) 580-2831.+18555802831.0..primaryPhone.cshPhone.1623143943.1623153362.600.10800.30.1....0....1...cubesmart^com.UA-1207651-2.1605234886^1620488575.35.; _gat=1; _gat_UA-1207651-2=1; nlbi_2413170_2147483646=tuwzAm4OsVTmCvov/cPt3AAAAAD7gLVlAkEK6dhuxE94Aw5F",
    "_ga=GA1.2.1605234886.1620488575; _gcl_au=1.1.918372723.1620488576; aam_uuid_opt=06256971139219621033527052771413870466; _fbp=fb.1.1620488889828.1871037673; _pin_unauth=dWlkPVpUYzFZbVk1TmprdFlqYzBNQzAwTjJGaUxXSTNaakl0TWpRMU5EZGlORE14WkRWaQ; _st_bid=0939cf00-93d6-11eb-bc89-0f12746e63bb; aam_test=aam%3D3684620; LPVID=NiZDFkNDM3MWZjYTc4ZjBj; nlbi_2413170=m8eKVSbW9gsCoFy2/cPt3AAAAADR74Bhx+Ucmfsn4xBiqBpV; incap_ses_207_2413170=Mjn2cjJ5ymVnWIFxxGnfAiUnv2AAAAAAPOBPCSYbY58u8tWM28NJhA==; at_check=true; _gid=GA1.2.1342296470.1623140139; mboxEdgeCluster=38; AMCVS_FA78F19C55BA9FAA7F000101%40AdobeOrg=1; s_cc=true; incap_ses_530_2413170=MlUdUTdBuTBYWuzvmfBaB5Asv2AAAAAAKuu5Z49I82m1DSDsuUElxQ==; search_term=; LPSID-22469663=MYs3IRP-S4-VNZM7yoCaTw; ASP.NET_SessionId=w4wiwhjz1dxke3qqdnjjlj5o; incap_sh_2413170=ED6/YAAAAABnxbl1DAAIkPz8hQYQi/z8hQZdb3DgZ13VJJAWlav/qdkR; visid_incap_2413170=UYWZywgMT9G57YsgP8C2+bOwlmAAAAAAREIPAAAAAACAkcmcAS0rDkz5Zdu1NGb7+PGnzYXwtljz; _usiTracking=9572728; AMCV_FA78F19C55BA9FAA7F000101%40AdobeOrg=-637568504%7CMCIDTS%7C18787%7CMCMID%7C06220023048075832883530184630691412429%7CMCAAMLH-1623750820%7C7%7CMCAAMB-1623750820%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1623153220s%7CNONE%7CvVersion%7C5.1.1%7CMCAID%7CNONE; _ce.s=v11.rlc~1623144670965~v11slnt~1623146021984; _gat_UA-1207651-2=1; _gat=1; _uetsid=b9a12b80c83111eb960a53c56458616a; _uetvid=13679d00b01411eb8b98e188bf556b85; nlbi_2413170_2147483646=uUkEG8Z47C/OaSbk/cPt3AAAAAA03e+K/4Uvq++9K/xwzGOv; reese84=3:ufBtWj3432XGVNhsgtPMGA==:JQQrb+qEK0UbsX99wuWKAQFm9jdakNF780VBoCORwVZCj5ICfysNnYTlV0tHGie5a7NAiSGz5bXX/bReSp3draxgxVHb94T2D5Q7jTjuyOR6jdxofeskY99pHaVCIAbCC/r0sK2nl/zUAfs9IXfyjsvqcVx/UwFIZb7zunK326qtdxitpMvADKmoQWukkGwYmy6yr8ZKIFIlVkb5fIrmSgalEtb2VrbOtYL0faRAHDk+USN5MW3Eq1jXcO7EKpVKWZYOJtyoGUDuF5j9xMs0FrRZuGbwETYmluiao9LQ0Lv8/LZwfBtkXgQVTEEyJE8OR0lvYDOHpjZVjQcS4uWVCrmWXxsoDjepLwqhD8JGl3ytNAIbymAGf0HXqQkCfXzYPTzlK21tKehxaAwK/pHjED6pRxBYGuc1lb2MCP4//8M=:0kHWP3za6nbPLqdua/MVX4T2Khvl9jc23FpfofBGROA=; mbox=PC#ecd6e123c41646ee84167cc509812e27.38_0#1686390980|session#267176b0bc6d4216a30b036b3490979f#1623146521; gpv_pageName=facility%3A5083%3A3333%20meade%20ave%20las%20vegas%20nv%2089102; s_sq=%5B%5BB%5D%5D; s_plt=19.32; s_pltp=facility%3A5083%3A3333%20meade%20ave%20las%20vegas%20nv%2089102; _st=0939cf00-93d6-11eb-bc89-0f12746e63bb.c1513710-c831-11eb-8a62-a95a6f722872.8555802831.(855) 580-2831.+18555802831.0..primaryPhone.cshPhone.1623146802.1623150959.600.10800.30.1....0....1...cubesmart^com.UA-1207651-2.1605234886^1620488575.35.",
    "_ga=GA1.2.1605234886.1620488575; _gcl_au=1.1.918372723.1620488576; aam_uuid_opt=06256971139219621033527052771413870466; _fbp=fb.1.1620488889828.1871037673; _pin_unauth=dWlkPVpUYzFZbVk1TmprdFlqYzBNQzAwTjJGaUxXSTNaakl0TWpRMU5EZGlORE14WkRWaQ; _st_bid=0939cf00-93d6-11eb-bc89-0f12746e63bb; _usiTracking=4064102; aam_test=aam%3D3684620; LPVID=NiZDFkNDM3MWZjYTc4ZjBj; visid_incap_2413170=UYWZywgMT9G57YsgP8C2+bOwlmAAAAAAQ0IPAAAAAACAd4ucAS0rDlZpxsTZ82QF9tfjVvE9tKLY; nlbi_2413170=m8eKVSbW9gsCoFy2/cPt3AAAAADR74Bhx+Ucmfsn4xBiqBpV; incap_ses_207_2413170=Mjn2cjJ5ymVnWIFxxGnfAiUnv2AAAAAAPOBPCSYbY58u8tWM28NJhA==; at_check=true; _gid=GA1.2.1342296470.1623140139; mboxEdgeCluster=38; AMCVS_FA78F19C55BA9FAA7F000101%40AdobeOrg=1; s_cc=true; incap_ses_530_2413170=MlUdUTdBuTBYWuzvmfBaB5Asv2AAAAAAKuu5Z49I82m1DSDsuUElxQ==; search_term=; LPSID-22469663=MYs3IRP-S4-VNZM7yoCaTw; _ce.s=v11.rlc~1623142541578~v11slnt~1623141535561; AMCV_FA78F19C55BA9FAA7F000101%40AdobeOrg=-637568504%7CMCIDTS%7C18787%7CMCMID%7C06220023048075832883530184630691412429%7CMCAAMLH-1623748468%7C7%7CMCAAMB-1623748468%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1623150868s%7CNONE%7CvVersion%7C5.1.1%7CMCAID%7CNONE; gpv_pageName=facility%3A5904%3A312%20n%20gay%20st%20auburn%20al%2036830; s_sq=%5B%5BB%5D%5D; ASP.NET_SessionId=w4wiwhjz1dxke3qqdnjjlj5o; _uetsid=b9a12b80c83111eb960a53c56458616a; _uetvid=13679d00b01411eb8b98e188bf556b85; mbox=PC#ecd6e123c41646ee84167cc509812e27.38_0#1686388528|session#0bd6512fa8674eeba4afa608d5a1b409#1623144394; s_plt=6.51; s_pltp=facility%3A5904%3A312%20n%20gay%20st%20auburn%20al%2036830; _st=0939cf00-93d6-11eb-bc89-0f12746e63bb.c1513710-c831-11eb-8a62-a95a6f722872.8555802831.(855) 580-2831.+18555802831.0..primaryPhone.cshPhone.1623145230.1623150959.600.10800.30.1....0....1...cubesmart^com.UA-1207651-2.1605234886^1620488575.35.; nlbi_2413170_2147483646=4oVMO49GHgWpMUIP/cPt3AAAAABcv0yqfV7uwgDZ2oCyFJMP; reese84=3:ZD3LBgLWADwlUmnp2+RuvA==:OvBMjazjrG/EP76kDKdcBCjwNw80lb/Y+Pzo+GFrTkeLUnuSqJ8JtgYzZdho3CQJZ0MTovWDzcLw1J7mJgoP0aYvA7VK6Q24yHHWAeJyUw92mcNnNzdvMARgM8qGkZGEEYuiunWUF2duFQiUJ9nTCCGdEBLmDa0f5JPGBNYKFRf2tEFtVf4SqDhibSuw0Se9NspxFEOw5RVOgY3yVz5907QVJ0Wb2ugieEGR9UCZwca/AfIRD6J0hXeNDDf9+UVT1m5rKtnTB82/JdQ+Q049JN5r6LFpoaySS4F9dlMU/URXIKyAce57qlIyGtUQZ7/sNROah9FmJ1+YQCSyirHZTQDo40+1E/P9keMmuy2YpaRhoR2hKiuo36qDLp4NJbyPsUjUPV4CEK80PYtrxdZ86Cfvlx12fuq9RJblIXXYF+A=:4H+EiE9AlvMZ0yu1tDilY73b827OlqS+7wCZG4nAgV4=",
]
headers1 = {
    "Host": "www.cubesmart.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}


def write_output(data):

    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    data = []
    p = 0
    url = "https://www.cubesmart.com/facilities/query/GetSiteGeoLocations"
    storelist = []
    try:
        loclist = session.post(url, headers=headers, verify=False).json()
    except:
        headers["Cookie"] = cookielist[1]
        loclist = session.post(url, headers=headers, verify=False).json()
    for loc in loclist:
        store = str(loc["Id"])
        street = loc["Address"]
        title = "Self Storage of " + loc["City"]
        city = loc["City"].lower().strip().replace(" ", "-")
        state = loc["State"]
        lat = loc["Latitude"]
        longt = "-" + str(loc["Longitude"])
        link = (
            "https://www.cubesmart.com/"
            + state
            + "-self-storage/"
            + city
            + "-self-storage/"
            + store
            + ".html"
        )
        if street in storelist:
            continue
        storelist.append(street)

        headers1["Cookie"] = cookielist[1]
        headers1["Referer"] = (
            "https://www.cubesmart.com/"
            + state
            + "-self-storage/"
            + city
            + "-self-storage/"
        )

        r = session.get(link, headers=headers1).text
        try:
            pcode = r.split(',"postalCode":"', 1)[1].split('"', 1)[0]
        except:

            headers1["Cookie"] = cookielist[2]
            r = session.get(link, headers=headers1).text
            try:
                pcode = r.split(',"postalCode":"', 1)[1].split('"', 1)[0]
            except:
                continue
        phone = r.split('},"telephone":"', 1)[1].split('"', 1)[0]
        try:
            hours = (
                r.split('<p class="csHoursList">', 1)[1]
                .split("</p>", 1)[0]
                .replace("&ndash;", " - ")
                .replace("<br>", " ")
                .lstrip()
            )
        except:
            hours = "<MISSING>"
        if pcode == "75072":
            pcode = "75070"
        if loc["OpenSoon"] == False:
            data.append(
                [
                    "https://www.cubesmart.com/",
                    link,
                    title,
                    street,
                    str(loc["City"]),
                    str(loc["State"]),
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours.replace("<br/>", " ").strip(),
                ]
            )

            p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
