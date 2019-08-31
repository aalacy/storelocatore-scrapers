const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://www.tcbk.com/_/api/branches/36.778261/-119.41793239999998/500';
async function scrape(){

return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{

                if(!err && res.statusCode==200){
            
                var ref = JSON.parse(res.body);
                var ref1 = ref.branches;

                const $  =cheerio.load(html);
            
                
                    var items=[];

                    function mainhead(i)

                    {
                        if(ref1.length>i)

                            {

                            var obj = ref1[i];
                            var address = obj.address;
                            var location_name = obj.name;
                            var city = obj.city;
                            var state = obj.state;
                            var zip = obj.zip;
                            var phone = obj.phone;
                            var longitude = obj.long;
                            var lattitude = obj.lat;
                            var hour_temp =  obj.description;
                            var hour = hour_temp.replace(/<[^>]+>/g, '').replace('Hours','');

                                items.push({
                                locator_domain : 'https://www.tcbk.com/',
                                location_name : location_name,
                                street_address : address,
                                city:city,
                                state:state,
                                zip:zip,
                                country_code: 'US',
                                store_number:'<MISSING>',
                                phone:phone,
                                location_type:'tcbk',
                                latitude:lattitude,
                                longitude :longitude,
                                hours_of_operation:hour
                                });  
                
     
                             mainhead(i+1);

                            }
     

                            else{
                        
                            resolve(items);
                        
                            }
                     } 
  
                 mainhead(0);

            }

    
      });
  });


}

 Apify.main(async () => {

const data = await scrape();

  await Apify.pushData(data);
      
 });
 
