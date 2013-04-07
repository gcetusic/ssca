$(document).ready(function () {
	$('.dropdown-menu a').attr('tabindex', -1);
	$('.dropdown-menu a').click(function (e) {
        e.preventDefault();
        moveTabsAndContents();
        var pageType = $(this).data("page-type");
        
        if(pageType == 'maps')
            Dajaxice.app_public.sscamaps_ajax(load_maps);
        else{
            
            Dajaxice.app_public.sscapage_ajax(load_page, {'page': this.getAttribute('href')});
        }
		  
		return false;
	});
})

// function for moving tabs and its contents
function moveTabsAndContents() {
    var contents = $('.tab-contents');
    var headers = $('.tab-headers');
    var headers_length = $('.tab-headers').length;
    for(var i=headers_length-1; i >= 0; i--) {
        if(i != 3){
            $(headers[i+1]).text($(headers[i]).text());
            $(contents[i+1]).html($(contents[i]).html());
        }
    }
    $('.sub-pagleft').hide();
    $('.in .sub-pagleft').show();
}


function load_page(page) {
	var page_html = page.content;
	var div = document.createElement('div');
	div.innerHTML = page_html;

	$("#page_title").fadeToggle(function () {
		$(this).html(page.title);
		$(this).fadeToggle();
	});

	$("#page_content").fadeToggle(function () {
		// add id to every image inside content and check if scrolled to it
		$(div).find("img").attr("id", "content_img");
		$(document).scroll(function () {
			console.log("scrolled");
		});

		$(this).html(div);
		$(this).fadeToggle();
	});

	$("#page_picture").fadeToggle(function () {
		$(this).html(page.picture);
		$(this).fadeToggle();
		$(this).children('img').addClass('img-rounded');
	});
    $('#myTab a:first').tab('show');
}

function load_maps(maps) {
    $('#page_content').fadeToggle(function() {
        $(this).html(maps);
        loadScript;
    });
}


function loadScript() {
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.src = "http://maps.googleapis.com/maps/api/js?key={{ google_maps_key }}&sensor=true&callback=initialize";
    $('.content').append(script);
}
