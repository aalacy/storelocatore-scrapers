const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
const zipcode=require('zipcodes')
const { getCode,getName } = require('country-list');
async function scrape(){
    return new Promise(async (resolve,reject)=>{
        request('https://carpetspluscolortile.com/wp-admin/admin-ajax.php?action=store_search&lat=35.0456297&lng=-85.30968009999998&max_results=25&search_radius=50&autoload=1',(err,res)=>{
            if(!err && res.statusCode==200){
                var ref = JSON.parse(res.body);
                var items=[];
                for(var i = 0; i < ref.length; i++) {
                    var obj = ref[i];
                    var city = obj.city;
                    var address = obj.address;
                    var temp_location_name = obj.store;
                    var location_name = temp_location_name.replace("#038;",'' ).replace("&#8211;",'-').replace("&#8217;","");
                    var state = obj.state;
                    var zip = obj.zip;
                    var store_number = obj.id;
                    var phone = obj.phone;
                    var longitude = obj.lng;
                    var lattitude = obj.lat;
                    var hour_temp =  obj.hours;
                    if(hour_temp){
                        var hour = hour_temp.toString().replace(/<[^>]+>/g, '') ;
                    } 
                    else{
                        var  hour = '<MISSING>';
                    }
                    items.push({
                        locator_domain : 'https://carpetspluscolortile.com/',
                        location_name : location_name,
                        street_address : address,
                        city:city,
                        state:state,
                        zip:zip,
                        country_code: 'US',
                        store_number:store_number,
                        phone:phone,
                        location_type:'carpetspluscolortile',
                        latitude:lattitude,
                        longitude :longitude,
                        hours_of_operation:hour
                    }); 
                }
                resolve(items);
            }    
        });
    })
}
Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});
