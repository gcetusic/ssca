$(document).ready(function () {
	$('.dropdown-menu a').attr('tabindex', -1);
	$('.dropdown-menu a').click(function () {
        moveTabsAndContents();
		Dajaxice.app_public.sscapage_ajax(load_page, {'page': this.getAttribute('href')});
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
	$("#page_title").fadeToggle(function () {
		$(this).html(page.title);
		$(this).fadeToggle();
	});

	$("#page_content").fadeToggle(function () {
		$(this).html(page.content);
		$(this).fadeToggle();
	});

	$("#page_picture").fadeToggle(function () {
		$(this).html(page.picture);
		$(this).fadeToggle();
		$(this).children('img').addClass('img-rounded');
	});
    $('#myTab a:first').tab('show');
}
