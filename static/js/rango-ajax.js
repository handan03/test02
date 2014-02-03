$(document).ready(function() {

     	$('#likes').click(function(){
    	var catid;
    	catid = $(this).attr("data-catid");
     	$.get('/rango/like_category/', {category_id: catid}, function(data){
               $('#like_count').html(data);
               $('#likes').hide();
           });
	});

	$('#suggestion').keyup(function(){
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {suggestion: query}, function(data){
         $('#cats').html(data);
        });
	});


    $('.btn-mini').click(function(){
        
	var url = $(this).attr("data-url");
    	var catid = $(this).attr("data-catid");
    	var title = $(this).attr("data-title");
	var spanid = "#" + $(this).attr("data-id");
//	var buttonid = "#_" + spanid;

//        var me =$(this)
	$.get('/rango/auto_add_page/', {"category_id": catid, "url": url, "title": title},function(data){
//        $.get('/rango/auto_add_page/',{category_id:catid,url:url,title:title},function(data){
                $(spanid).hide();
//                $(buttonid).hide();
                $(spanid).remove();
//                $(buttonid).remove();
//            $('#addpage').html(data);
//            $('#addpage').hide();
	});
    });




});