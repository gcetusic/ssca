$(document).ready(function () {
	$('.dropdown-menu a').attr('tabindex', -1);
	$('.dropdown-menu a').click(function () {
		Dajaxice.app_public.sscapage_ajax(load_page, {'page': this.getAttribute('href')});
		return false;
	});
})


function load_page(page) {
	$('#page_title').html(page.title);
	$('#page_content').html(page.content);
	$('#page_picture').html(page.picture);
	$('#page_picture > img').addClass('img-rounded');
}
