<?php

function remove_config($config_file) {
    if (file_exists($config_file)) {
        $doc = new DOMDocument; 

        $doc->load($config_file);

        $thedocument = $doc->documentElement;

        //this gives you a list of the messages
        $list = $thedocument->getElementsByTagName('hudson.model.StringParameterDefinition');
        if ($list != null) {
            //figure out which ones you want -- assign it to a variable (ie: $nodeToRemove )
            foreach ($list as $domElement){
                try {
                    $thedocument->removeChild($domElement);
                } catch (Exception $e) {
                    echo "{$e->getMessage()}\n";
                    continue;
                }
            }


            file_put_contents($config_file, $doc->saveXML());
        }
    }
}

function main() {
    $fileString = `ls -d Build_*/config.xml`;

    $fileList = explode("\n", $fileString);
    foreach($fileList as $config_file) {
        echo "Updateing file ... $config_file\n";
        remove_config($config_file);
    }
}

main();
