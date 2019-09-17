const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://locations.dashin.com';

async function scrape(){

return new Promise(async (resolve,reject)=>{
request(url,  function(err,res,html){

   if(!err && res.statusCode==200){
      
       const $  =cheerio.load(html);
      
       var main = $('.container').find('.col-xs-12').find('.lm-col-3');
      // console.log(main.length);
      
     
       var items=[];

       function mainhead(i)

            {

                if(main.length>i)

                {
 
      
         const link = url+ main.eq(i).find('a').attr('href');
        // console.log(link);
        
          request(link,function(err,res,html){    
             if(!err && res.statusCode==200){
               const $ =cheerio.load(html);
               var main2=$('.lm-homepage__states-container').find('.container').children();
              

               function mainhead1(i1){

                if(main2.length>i1)

                {
                  const link2 = $('.lm-homepage__states-container').find('.container').find('.col-xs-12').eq(i1).children();

                 //const link2 = main2.find('.col-xs-12').eq(i1).children();
                 
            //console.log(link2.length);
                 

                 function mainhead2(i2){

                  if(link2.length>i2)

                  {
                     
             
                       const link3=url+link2.eq(i2).find('a').attr('href');
                       
                      // console.log(link3);
                     

                  
                          request(link3,async function(err,res,html){    
                              if(!err && res.statusCode==200){
                                const $ =cheerio.load(html);
                                var main3_temp =$('.lm-business-detail__store-info').find('.lm-list-item__details').children();
                                function mainhead3(i3){

                                  if(main3_temp.length>i3)

                                  {
                                var main3_temp1 = main3_temp.find('p').html();
                                var main3_temp2 =main3_temp1.split('<br>');
                                var address =main3_temp2[0];
                                var city_temp = main3_temp2[1];
                                var city_temp1 =city_temp.split(' ');
                                
                                if(city_temp1.length == 3){
                                  var city = city_temp1[0];
                                  var state = city_temp1[1];
                                  var zip = city_temp1[2];

                                }
                                else if(city_temp1.length == 4)
                                {
                                  var city = city_temp1[0]+city_temp1[1];
                                  var state = city_temp1[2];
                                  var zip = city_temp1[3];
                                }
                
                                    var hour_temp =   $('.lm-business-detail__store-info').find('.lm-col-3').eq(1).text().trim();
                                    var hour = hour_temp.replace(/ +(?= )/g, "").replace(/\n+/g, "").replace('     ','').trim();
                                    
                                   
                                    var phone =  $('.lm-business-detail__store-info').find('.lm-col-3').find('.lm-list-item__detail-item').find('span').find('a').text().trim();
                                    var location_name_temp = $('.lm-breadcrumb').find('.lm-breadcrumb-list-item:last-child').find('a').find('span').text().trim();
                                    var location_name =location_name_temp.replace("Dash In","");
                                    var latitude_temp =  $('script[type="application/ld+json"]').html();
                                    var latitude_temp1 =  JSON.parse(latitude_temp);
                                    var latitude = latitude_temp1.geo.latitude;
                                    var longitude = latitude_temp1.geo.longitude;
                
                                      items.push({ 

                                          locator_domain: url, 
                                          location_name:location_name,
                                          street_address: address,
                                          city: city,
                                          state: state,
                                          zip: zip,
                                          country_code: 'US',
                                          store_number: '<MISSING>',
                                          phone: phone, 
                                          location_type: 'dashin', 
                                          latitude: latitude, 
                                          longitude: longitude, 
                                          hours_of_operation: hour
                                        });
 
                  
                                     //  console.log(items);
                                                              mainhead3(i3+1);

                                                            }

                                                        else{

                                                        mainhead2(i2+1);

                                                        }

                                                      }

                                                mainhead3(0);
                                                  }//index3 if
                                                  
                                              });//index 3 req

                                             }//function 3 if

                                          else{

                                                mainhead1(i1+1);

                                              }

                                       }//function 3

                                     mainhead2(0);
                                              
                                          
                                        }//function 2 if

                        else{

                           mainhead(i+1);

                        }

                     }//function 2
                        
                      mainhead1(0);

                   }//index2 if
                  });//index 2 req

       
                }//function 1 if

            else{
   
                resolve(items);

               }
          }//function 1

        mainhead(0);
      }//index1 if

   }); // index1 req
 });

}


 

    

Apify.main(async () => {
    const data = await scrape();
   
    await Apify.pushData(data);
});
