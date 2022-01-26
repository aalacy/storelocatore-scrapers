from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("curves_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=None,
)


def fetch_data():
    ids = [
        "https://www.wellnessliving.com/fitness/aiea/aieahi-0nvvmz/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/windsor/windsorca-4ts6gw/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/santarosa/santarosaca-northeast-g0mprg/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/petaluma/petalumaca-east-w4or5a/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/sanrafael/sanrafaelca-5mx36t/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/walnutcreek/walnutcreekca-south-5r5tlw/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/concord/concordca-south-lkw4vn/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/losaltos/losaltosca-e54hn9/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/sanjose/sanjoseca-campbell-8wq90q/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/santacruz/santacruzca-3jc3di/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/aptos/aptosca-fmaa7n/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/prunedale/prunedaleca-axl6kd/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/dixon/dixonca-79rp6a/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/santabarbara/santabarbara-westgoletaca/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/elkgrove/elkgroveca-cosumnesriver-ymffpv/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/modesto/curvesmodestoca/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/sacramento/sacramentoca-arena-duafje/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/redding/reddingca-west-mn01z3/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/thousandoaks/thousandoaksca-north-mxxsag/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/fairoaks/citrusheightsca-liqqv1/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/merced/mercedca-5xpnet/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/roseville/rosevilleca-southwest-lnk0c0/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/madera/maderaacresca-9wwx41/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/paradise/paradiseca-to7m6p/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/torrance/torranceca-central-xytzm5/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/losangeles/losangelesca-marinadelreysouth-g7g9ct/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/pasadena/pasadenaca-north-clhai1/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/bellflower/bellflowerca-46burt/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/monrovia/monroviabradburyduarteca-l5phyg/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/fresno/fresnoca-eastcentral-ajhvko/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/gardengrove/gardengroveca-southwest-mvled5/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/ranchosantamargarita/ranchosantamargaritaca-stzftu/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/pomona/claremontca/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/corvallis/curvescorvallisor/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/riverside/downtownriversideca-cgw9po/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/monmouth/monmouthindependenceor-t443kw/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/newberg/newbergor-frnkd2/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/aloha/alohaor-wqulop/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/vancouver/orchardswa-sseycl/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/indio/bermudadunesca-mj2v7e/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/tumwater/tumwaterwa-9kao0r/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/dayton/daytonnv-vu50sm/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/twentyninepalms/twentyninepalmsca-kgswjc/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/tacoma/tacomawa-northwest-lrdeqr/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/federalway/federalwaywa-south-erbesw/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/glendale/phoenixaz-northwestcentral-optnui/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/gilbert/gilbertaz-west-6oqnvm/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/coolidge/coolidgeaz-rxi2o5/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/nampa/nampaid-g5we5r/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/boise/boiseid-southwest-ufc0cm/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/ponderay/sandpointid-ttckcy/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/libby/libbytroymt-zzr1k1/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/orem/oremut-olhnf7/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/lehi/lehicedarforteaglemountainsaratogaspringsut-evuyz2/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/pleasantgrove/pleasantgrovelindonut-54oxeh/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/saltlakecity/cottonwoodheightsut-xsi8co/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/odessa/odessatx-east-bj1kal/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/riverton/rivertonwy-j9ktp7/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/coloradosprings/coloradospringsco-central-3kut9h/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/coloradosprings/coloradospringsco-cimarronhills-rb4q5u/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/arvada/arvadaco-east-rrxzan/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/austin/austintx-wellsbranch-ajves7/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/loveland/lovelandco-uheuy1/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/lampasas/lampasastx-onqtmh/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/taylor/taylortx-tso6sl/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/houston/houstontx-memorial-8dhygs/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/houston/springvalleytx-r64lyf/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/waco/woodwayhewittmcgregortx-nnrtz2/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/spring/houstontx-kleinwest-zn0lmi/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/conroe/conroetexas-north-ipanfk/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/huntsville/huntsvilletx-gmhgdo/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/arlington/arlingtontx-southeast-sx25qd/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/silsbee/silsbeelumbertontx-u80ibq/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/richardson/richardsontx-east-4awnih/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/plano/planotx-southwest-7dna6x/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/northplatte/northplattene-nyzbkl/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/thibodaux/thibodauxla-pvtuoj/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/brookhaven/brookhavenms-bspdx8/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/seminole/seminolefl-cfxltr/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/olathe/olatheks-east-1b0008/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/melbourne/melbournefl-central-6yebxf/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/kansascity/kansascitymo-redbridge-9dmtco/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/winterpark/winterparkfl-west-myepsl/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/santarosabeach/santarosabeach_fl/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/liberty/libertymo-2l9dut/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/alexandria/alexandriamn-sd8r9k/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/memphis/memphistn-southeast-pav3bb/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/staples/staplesmn-6c0vxa/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/montgomery/montgomeryal-east-gkypri/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/littlefalls/littlefallsmn-pkpuav/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/brooklyncenter/brooklyncentermn-oro3nz/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/falconheights/falconheightsmn-18brd2/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/ballwin/ballwinmo-swnmgu/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/manchester/manchestermo-hwnkzw/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/saintcharles/saintcharlesmo-newtown-iwsypo/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/riverfalls/riverfallswi-6sluvs/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/cloquet/cloquetmn/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/meridianville/hazelgreenmeridianvilleal-5clcki/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/peachtreecity/peachtreecityga-bsdj73/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/cedarrapids/cedarrapidsia-west-9et7qe/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/coralville/coralvillenorthlibertyia-5w8jne/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/benton/bentonil-6fntul/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/onalaska/onalaskawi-iopxfg/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/clarksville/sangotn-lnmye6/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/dacula/daculaga-ba5lav/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/cumming/cummingga-north-7zgm18/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/soddydaisy/soddydaisytn-rfbaz3/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/peoria/peoriail-west-jlm1tl/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/monticello/monticelloil-oeofu5/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/oregon/oregonil-fkv5ck/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/monckscorner/monckscornersc-utwm4l/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/champaign/champaign-southsavoyil-pr98wg/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/greenville/greenvillesc-east-ztjmui/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/watertown/watertownwi-75lxql/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/oconomowoc/oconomowocwi-g6lzqy/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/ingleside/inglesideil-kb2ytq/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/elmhurst/elmhurstil-south-lcrg8d/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/elkgrovevillage/elkgrovevillageil-5bapii/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/crete/creteil-cesarc/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/franklin/franklinwi/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/menomoneefalls/menomoneefallswi-1r1nse/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/chicago/chicagoil-edgewater-a2ba40/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/milwaukee/wauwatosawi-east-eeqy3v/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/oakcreek/oakcreekwi-4cvy2q/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/sheboyganfalls/sheboyganfallswi-yitfe1/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/indiantrail/indiantrailnc-mkt8wo/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/matthews/minthillmatthewsnc-h5z5kd/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/lexington/lexingtonky-east-cazdy8/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/mooresville/curvesmooresvillenc/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/bristol/bristoltn-sxuniw/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/cincinnati/cincinnatioh-finneytown-nljipv/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/yadkinville/yadkinvillenc-hroynm/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/sharonville/westchesteroh-east-grsxpl/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/centerville/centervilleoh-west-kxznew/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/wytheville/wythevilleva-vyfkev/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/raleigh/raleighnc-capitalcommons-z5xqhc/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/lima/limaoh-szofel/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/rockymount/rockymountva-zfybbv/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/westerville/columbusoh-northeast-8erclb/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/spencer/spencerwv-ssptoj/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/plymouth/plymouthmi-zmwlru/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/mansfield/mansfieldontariooh-1geh5h/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/caldwell/caldwelloh-ux6pqm/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/virginiabeach/virginiabeachva-generalbooth-prgntb/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/staunton/stauntonveronava/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/eastpointe/eastpointemi-b19gce/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/glenallen/glenallenva-v2lsen/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/stafford/staffordva-courthouse-vzzpdc/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/carnegie/collierheidelbergscottpa-33zbzc/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/ambridge/sewickleyedgeworthleetleetsdalepa-8lkgvv/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/apollo/washingtontownshippa-yjfiya/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/lanham/glenndalemd-hlytgh/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/columbia/columbiamd-west-e3il3l/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/baltimore/whitemarshmd-cil4sa/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/dublin/dublinhilltownpa-cw82o7/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/bloomsburg/bloomsburgpa-2mti2m/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/greenbrook/northplainfieldgreenbrooktownshipnj-r2zoet/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/longbeach/longbeachislandparkny-qbs0d4/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/flushing/queensny-whitestonemurrayhill-emlqlq/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/sayville/sayvilleny-iltnbs/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/monroe/monroeny-frarkn/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/montgomery/montgomeryny-albxm2/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/webster/websterma-25kncy/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/topsfield/topsfieldma-2qwf0z/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/westbrook/westbrookportlandme-foj0xk/review/?id_mode=12",
        "https://www.wellnessliving.com/fitness/londonderry/londonderrytownshipnh-hxsbzr/review/?id_mode=12",
    ]

    for clat, clng in search:
        logger.info(str(clat) + "-" + str(clng))
        url = (
            "https://www.curves.com/find-a-club?location=10002&lat="
            + str(clat)
            + "&lng="
            + str(clng)
        )
        try:
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                if ">&#x1F4DE;</i>" in line:
                    phone = line.split(">&#x1F4DE;</i>")[1].split("<")[0]
                if '<a href="https://www.wellnessliving.com' in line:
                    curl = line.split('href="')[1].split('"')[0]
                    if curl not in ids:
                        ids.append(curl)
        except:
            pass
    for purl in ids:
        r2 = session.get(purl, headers=headers)
        name = ""
        website = "curves.com"
        typ = "Fitness Studio"
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "US"
        store = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        for line2 in r2.iter_lines():
            if '<meta name="geo.position" content="' in line2:
                lat = line2.split('<meta name="geo.position" content="')[1].split(";")[
                    0
                ]
                lng = (
                    line2.split('<meta name="geo.position" content="')[1]
                    .split(";")[1]
                    .split('"')[0]
                )
            if '"geo.placename" content="' in line2:
                name = line2.split('"geo.placename" content="')[1].split('"')[0]
            if 'margin:0;">  <li> <img alt="' in line2:
                typ = line2.split('margin:0;">  <li> <img alt="')[1].split(" in ")[0]
            if '<span itemprop="streetAddress">' in line2:
                add = line2.split('<span itemprop="streetAddress">')[1].split("<")[0]
                city = line2.split('itemprop="addressLocality">')[1].split("<")[0]
                state = line2.split('<span itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if 'class="css-flex css-item-between">' in line2:
                days = line2.split('class="css-flex css-item-between">')
                for day in days:
                    if (
                        '<div class="css-flex css-flex-column"><span>' in day
                        or '<span class="today">' in day
                    ):
                        hrs = (
                            day.split("</span>")[0].rsplit(">", 1)[1]
                            + ": "
                            + day.split("</span></div>")[0].rsplit(">", 1)[1].strip()
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        add = add.replace("&amp;", "&")
        city = city.replace("&amp;", "&")
        name = name.replace("&amp;", "&")
        if add != "":
            yield SgRecord(
                locator_domain=website,
                page_url=purl,
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
