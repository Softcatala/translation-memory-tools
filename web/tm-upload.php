<?php

function showStatistics($filename)
{
	$command = "msgfmt -o /dev/null --statistics " . $filename . " 2>&1";
	
	exec($command, $output, $return_value);	
	echo "<br/><b>Resultats</b><br/>";
	echo $output[0];
}

function showLink($link)
{
	echo "<br/>Baixada: <a href=" . $link . ">" . $link . "</a>";	
}

/***
	Main
***/

	if ($_FILES["file"]["error"] > 0)
	{
		echo "Error: " . $_FILES["file"]["error"] . "<br>";
		die();
	}
	  
	$po_outdir = "output";
	  
	if ( !file_exists($po_outdir) ) {
		mkdir ($po_outdir, 0777);
	}
	 
	switch ($_POST["memory"])
	{
	case "gnome":
		$tm_file = "gnome-tm.po";
		break;
	case "fedora":
		$tm_file = "fedora-tm.po";
		break;
	case "mozilla":
		$tm_file = "mozilla-tm.po";
		break;
	case "libreoffice":
		$tm_file = "libreoffice-tm.po";
		break;
	default:
		$tm_file = "tm.po";
		break;
	}
	
	$uploaded_file = $_FILES["file"]["tmp_name"];
	$out_file = $_SERVER["DOCUMENT_ROOT"] . "/output/tm-" . $_FILES["file"]["name"];
	$tm_file = $_SERVER["DOCUMENT_ROOT"] . "/memories/" . $tm_file;
	$link = "http://recursos.softcatala.org" . "/output/tm-" . $_FILES["file"]["name"];
	
	$command = "msgmerge -N " . $uploaded_file . " " . $uploaded_file . " -C " . $tm_file . " > " . $out_file;	
	exec($command, $output, $return_value);
	
	showStatistics($out_file);
	showLink($link);

?> 
