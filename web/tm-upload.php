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

// Main

	if ($_FILES["file"]["error"] > 0)
	  {
	  echo "Error: " . $_FILES["file"]["error"] . "<br>";
	  }
	else
	  {
	#  echo "Upload: " . $_FILES["file"]["name"] . "<br>";
	#  echo "Type: " . $_FILES["file"]["type"] . "<br>";
	#  echo "Size: " . ($_FILES["file"]["size"] / 1024) . " kB<br>";
	#  echo "Stored in: " . $_FILES["file"]["tmp_name"];
	  }
	  
	$po_outdir = "output";
	  
	if ( !file_exists($po_outdir) ) {
	  mkdir ($po_outdir, 0777);
	 }
	
	$uploaded_file = $_FILES["file"]["tmp_name"];
	$out_file = $_SERVER["DOCUMENT_ROOT"] . "/output/tm-" . $_FILES["file"]["name"];
	$tm_file = $_SERVER["DOCUMENT_ROOT"] . "/tm.po";
	$link = "http://recursos.softcatala.org" . "/output/tm-" . $_FILES["file"]["name"];
	
	$command = "msgmerge -N " . $uploaded_file . " " . $uploaded_file . " -C " . $tm_file . " > " . $out_file;
	#echo $command;
	exec($command, $output, $return_value);
	
	showStatistics($out_file);
	showLink($link);


?> 
