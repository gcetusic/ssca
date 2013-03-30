function load_page(page) {
	$('#page_title').html(page.title);
	$('#page_content').html(page.content);
	console.log(page.picture);
	$('#page_picture').html(page.picture);
}
