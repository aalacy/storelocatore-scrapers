const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://www.epicwingsnthings.com/locations/';
 

async function scrape(){

return new Promise(async (resolve,reject)=>{ 
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
 
        const $  =cheerio.load(html);
        var items=[];

        var main = $('.location-list').children('li');
        function mainhead(i)

        {
            if(main.length>i)

                {
        
         


          var link = main.eq(i).find('a').attr('href');
        
          request(link,(err,res,html)=>{

            if(!err && res.statusCode==200){

              const $  =cheerio.load(html);
             var latitude = $('.marker').attr('data-lat');
             var longitude = $('.marker').attr('data-lng');
             var location_name = $('.col-xs-12').find('.row').find('.col-sm-6').find('h2').text().trim().replace('– NOW OPEN','');
             var hour = $('.hours').find('p').text().trim().replace(/<[^>]*>/g, '').replace('Restaurant Hours','').replace('Get DirectionsGuest Feedback','').trim().replace('\n','');
             var add_tmp =  $('.address').html();   
             var add_tmp1 = add_tmp.split('<br>');
             

            

                        if(add_tmp1.length == 3 ){
                          var address = add_tmp1[0].trim().replace(/<[^>]*>/g, '');
                          var city_tmp = add_tmp1[2].split('</p>');
                          var city_tmp1 = city_tmp[0];
                          var phone = city_tmp[1].trim().replace(/<[^>]*>/g, '');
                          var city_tmp2 = city_tmp1.split(',');
                          var city = city_tmp2[0].replace('\n',''); 
                          var state_tmp  = city_tmp2[1];
                          var state_tmp1 = state_tmp.split(' ');
                          var state = state_tmp1[1];
                          var zip = state_tmp1[2];

                          

                          
                        }

                          else if (add_tmp1.length == 2){
                            var address = add_tmp1[0].trim().replace(/<[^>]*>/g, '');
                            var city_tmp = add_tmp1[1].split('</p>');
                            var phone = city_tmp[1].trim().replace(/<[^>]*>/g, '');
                            var city_tmp1 = city_tmp[0];
                            var city_tmp2 = city_tmp1.split(',');
                            var city = city_tmp2[0].replace('\n',''); 
                            var state_tmp  = city_tmp2[1];
                            var state_tmp1 = state_tmp.split(' ');
                            var state = state_tmp1[1];
                            var zip = state_tmp1[2];
                          
                          }
                  
                                items.push({  

                                  locator_domain: 'https://www.epicwingsnthings.com/', 
                      
                                  location_name: location_name, 
                      
                                  street_address: address,
                      
                                  city: city, 
                      
                                  state: state,
                      
                                  zip:  zip,
                      
                                  country_code: 'US',
                      
                                  store_number: '<MISSING>',
                      
                                  phone: phone,
                      
                                  location_type: '<MISSING>',                                  
                      
                                  latitude: latitude,
                      
                                  longitude: longitude,

                                  hours_of_operation: hour,

                                  page_url:link 
                      
                              });

              mainhead(i+1);

          }// inn if
        });//inn req

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
