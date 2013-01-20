
<script>

function AjaxRequest()
{
	$('#resultat').html("S'està procesant...");
	
	var options = { target: '#resultat' };	
	$('#form').ajaxSubmit(options);
}

</script>
