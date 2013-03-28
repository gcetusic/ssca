$(document).ready(function () {
	$('.dropdown-menu a').attr('tabindex', -1);
	$('.dropdown-menu a').click(function () {
		Dajaxice.app_public.sscapage_ajax(load_page, {'page': this.getAttribute('href')});
		return false;
	});
})


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
}
