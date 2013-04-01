$(document).ready(function () {
	$('.dropdown-menu a').attr('tabindex', -1);
	$('.dropdown-menu a').click(function () {
		Dajaxice.app_public.sscapage_ajax(load_page, {'page': this.getAttribute('href')});
		return false;
	});
})


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
}
