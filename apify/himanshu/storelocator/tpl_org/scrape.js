const request=require('request');
const Apify = require('apify');
var items=[]
var stop=false
var cnt=1
var req=1

async function scrape(){
    return new Promise(async (resolve,reject)=>{
        setInterval(()=>{
            for(i=0;i<500;i++){
                if(req<500){
                    
                    req=req+1;
                    request(`https://server3.tplgis.org/arcgis3/rest/services/ParkServe/ParkServe_Parks/MapServer/0/${cnt}?f=pjson`,(err,res)=>{
                        try{
                            var data=JSON.parse(res.body)
                            console.log(data);
                            if(data.hasOwnProperty("error")){
                                stop=true
                                clearInterval(this)
                                resolve(items)
                            }
                            else{
                                items.push({
                                    locator_domain: "https://www.tpl.org",
                                    location_name:data["feature"]["attributes"]["Park_Name"]?data["feature"]["attributes"]["Park_Name"]:"<MISSING>",
                                    street_address: data["feature"]["attributes"]["Park_Address_1"]?data["feature"]["attributes"]["Park_Address_1"]:"<MISSING>",
                                    city:data["feature"]["attributes"]["Park_UrbanArea"]?data["feature"]["attributes"]["Park_UrbanArea"]: "<MISSING>",
                                    state:data["feature"]["attributes"]["Park_UrbanArea"]?data["feature"]["attributes"]["Park_UrbanArea"]:"<MISSING>",
                                    zip:"<MISSING>",
                                    country_code:"US",
                                    store_number:data["feature"]["attributes"]["ParkID"]?data["feature"]["attributes"]["ParkID"]:"<MISSING>",
                                    phone:"<MISSING>",
                                    location_type: "<MISSING>",
                                    latitude: "<MISSING>",
                                    longitude: "<MISSING>",
                                    hours_of_operation:"<MISSING>",
                                    page_url:`https://server3.tplgis.org/arcgis3/rest/services/ParkServe/ParkServe_Parks/MapServer/0/${cnt}?f=pjson`
                                });
                                req=req-1
                            }
                        }
                        catch(exce){
                            console.log('err');
                            
                        }
                    })
                    cnt=cnt+1;
                    console.log(cnt);
                }
            }
        },5000)
    });
}
Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});


//scrape();
