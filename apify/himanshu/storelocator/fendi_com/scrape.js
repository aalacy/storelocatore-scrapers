const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
 
 
var url = 'https://www.fendi.com/au/store-locator?listJson=true&country-selectize=&fendiType=BOUTIQUE&service=&line=&xlat=6.4626999&xlng=68.10969999999998&ylat=35.513327&ylng=97.39535869999997&country=IN';
async function scrape(){

  return new Promise(async (resolve,reject)=>{
 
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
   
     const $  =cheerio.load(html);
        var items=[];
        
        var ref = JSON.parse(res.body);
        var ref1 = ref[0];
        
        
        
        var address_tmp = ref1.address.line1;
        var address_tmp1 = address_tmp.split(',');
        var address = address_tmp1[0];
        var country_code = ref1.address.country.isocode;
        var city = ref1.address.town;
        var zip = ref1.address.postalCode;
        var location_name= ref1.displayName;
         
        var phone = ref1.address.phone;
        var hour_tmp = ref1.openingHours.weekDayOpeningList;
        var latitude = ref1.geoPoint.latitude;
        var longitude = ref1.geoPoint.longitude;
        
        var hour= " ";
        var i ;
       
        var hour_tmp1= [];
        function mainhead(i)

        {
            if(hour_tmp.length>i)

                {
                          var obj = hour_tmp[i];
                            var hour1 = obj.weekDay;
                            
                            
                            var hour2 = obj.openingHours;
                            
                            var hour3 = hour1.concat(hour2);
                            
                            
                            hour_tmp1.push(hour3);
                            
                    
                            mainhead(i+1);

                          }
   

                          else{
                      
                          resolve(items);
                      
                          }
                   } 

               mainhead(0);

            var hour = hour_tmp1.toString();
       
               items.push({
                    locator_domain : 'https://www.fendi.com/',
                    location_name : location_name,
                    street_address : address,
                    city:city,
                    state:'<MISSING>',
                    zip:zip,
                    country_code: country_code,
                    store_number:'<MISSING>',
                    phone:phone,
                    location_type:'fendi',
                    latitude:latitude,
                    longitude :longitude,
                    hours_of_operation:hour
                    
                    });  
                
        
        
         
            }
    });
  });
}

  
    
   
  
  Apify.main(async () => {
  
      
  
      const data = await scrape();
      
       
       await Apify.pushData(data);
    
    });