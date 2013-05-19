<?php
function update_config($config_file) {
    if (file_exists($config_file)) {
        $test_xml = simplexml_load_file($config_file);
        // Add new parameter 
/*
        $parameterDefintion = $test_xml->properties->{'hudson.model.ParametersDefinitionProperty'}->parameterDefinitions->addChild("hudson.model.StringParameterDefinition");
        $parameterDefintion->addChild("name", "version");
        $parameterDefintion->addChild("description");
        $parameterDefintion->addChild("defaultValue");

        $parameterDefintion->addChild("name", "branch");
        $parameterDefintion->addChild("description");
        $parameterDefintion->addChild("defaultValue", "master");

        $parameterDefintion->addChild("name", "package_list");
        $parameterDefintion->addChild("description");
        $parameterDefintion->addChild("defaultValue", "ent");

        $parameterDefintion->addChild("name", "upgrade_package");
        $parameterDefintion->addChild("description");
        $parameterDefintion->addChild("defaultValue", "0");

        $parameterDefintion->addChild("name", "author");
        $parameterDefintion->addChild("description");
        $parameterDefintion->addChild("defaultValue");

        $parameterDefintion->addChild("name", "styleguide_repo");
        $parameterDefintion->addChild("description");
        $parameterDefintion->addChild("defaultValue");

        $parameterDefintion->addChild("name", "styleguide_branch");
        $parameterDefintion->addChild("description");
        $parameterDefintion->addChild("defaultValue");

        $parameterDefintion->addChild("name", "sidecar_repo");
        $parameterDefintion->addChild("description");
        $parameterDefintion->addChild("defaultValue");

        $parameterDefintion->addChild("name", "sidecar_branch");
        $parameterDefintion->addChild("description");
        $parameterDefintion->addChild("defaultValue");

        // Add latin
        $parameterDefintion->addChild("name", "latin");
        $parameterDefintion->addChild("description");
        $parameterDefintion->addChild("defaultValue", "0");

        // Add demo_data
        $parameterDefintion = $test_xml->properties->{'hudson.model.ParametersDefinitionProperty'}->parameterDefinitions->addChild("hudson.model.StringParameterDefinition");
        $parameterDefintion->addChild("name", "demo_data");
        $parameterDefintion->addChild("description");
        $parameterDefintion->addChild("defaultValue", "1");
*/

        // Update old command
        $new_command = <<<'EOD'
rm -rf /dev/shm/sugarbuild-$version

#remove the submodule files
git ls-files --other --exclude-standard | xargs rm -rf

# handle submodules
cd sugarcrm
rm -rf ./styleguide
rm -rf ./sidecar
git clone $styleguide_repo
cd styleguide
git checkout $styleguide_branch
cd ..
git clone $sidecar_repo
cd sidecar
git checkout $sidecar_branch
cd ../..

# carry on with build
mkdir /dev/shm/sugarbuild-$version
cp -r sugarcrm /dev/shm/sugarbuild-$version/
cp -r build /dev/shm/sugarbuild-$version/
cp -r sugarportal /dev/shm/sugarbuild-$version/

cd /home/build/sugarsvn/Mango/build_clean
svn revert build_config.json
if [ "$upgrade_package" = 1 ]; then
  wget http://honey-g/BranchBuilder/buildconfig/buildconfig_get?version=$version -O build_config.json
  chmod 777 build_config.json
fi
./build_sugar_30.php --version $version --branch $branch  --deploy --packages "$package_list" --upgrades $upgrade_package --author "$author" --latin $latin --demo-data $demo_data 

rm -rf /dev/shm/sugarbuild-$version
EOD;
        $test_xml->builders->{'hudson.tasks.Shell'}->command = $new_command;

        // back_up config.xml as config.xml
        file_put_contents($config_file . ".bak", file_get_contents($config_file));
        file_put_contents($config_file, $test_xml->asXML());
    }
}

function update_restore() {

}

function main() {
    $options = getopt("ru", array(
        "restore",
        "update"
        ));
    var_dump($options);
    $fileString = `ls -d Build_*/config.xml`;

    $fileList = explode("\n", $fileString);
    if (isset($options["u"])) {
        echo "Updating... \n";
        foreach($fileList as $config_file) {
            update_config($config_file);
        }
    } else if (isset($options["r"])) {
        echo "Backuping... \n";
        foreach($fileList as $config_file) {
            if (file_exists($config_file . ".bak")) {
                file_put_contents($config_file . ".bak.bak", file_get_contents($config_file));
                file_put_contents($config_file, file_get_contents($config_file . ".bak"));
            }
        }
    } else {
            echo "do nothing\n";
    }
} 

main();
