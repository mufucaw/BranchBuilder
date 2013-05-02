#!/usr/bin/env ruby

# == Synopsis
#
# convert-existing-jobs.rb: Converts old Jenkins build job config.xml files specific to honey-g, adding new styleguide and sidecar
# parameters as well as disabling submodule processing
#
# == Usage
#
# convert-existing-jobs.rb [OPTIONS]
#
# --help, -h:
#   Display this helpful dialog :)
# --jobs_dir, -j:
#   Specify Jenkins jobs directory (required)
# --pattern, -p:
#   Specify a regex filter pattern, only jobs matching this pattern will be modified
# --mock, -m:
#   Mock changes but don't actually enact them. Prevents hair loss on production machines!
# --backup, -b:
#   Back up config.xml files prior to changing them providing the --mock option is absent. FEED your paranoia!
# --restore, -r:
#   Restore config.xml files to their original state ONLY if --backup was used to convert them and only if the --mock option is absent.
#
#
# EXAMPLES:
#
# ruby convert-existing-jobs.rb --jobs_dir /home/build/Jenkins/jobs --pattern ^Build\_ --mock
# Prints every job starting with "Build_" in /home/build/Jenkins/jobs to indicate  which jobs would have been modified.
#
# ruby convert-existing-jobs.rb --jobs_dir /var/lib/jenkins/jobs --backup
# Converts ALL jobs in /var/lib/jenkins/jobs but backs up every config.xml file first.
#
# ruby convert-existing-jobs.rb --jobs_dir /var/lib/jenkins/jobs --restore
# Restores all config.xml files to their pristine original state prior to running the previous example.

# includes
require 'getoptlong'
require 'rdoc/usage'
require 'fileutils'
require 'rexml/document'

# define command-line options
opts = GetoptLong.new(
  ['--help', '-h', GetoptLong::NO_ARGUMENT],
  ['--jobs_dir', '-j', GetoptLong::REQUIRED_ARGUMENT],
  ['--pattern', '-p', GetoptLong::REQUIRED_ARGUMENT],
  ['--mock', '-m', GetoptLong::NO_ARGUMENT],
  ['--backup', '-b', GetoptLong::NO_ARGUMENT],
  ['--restore', '-r', GetoptLong::NO_ARGUMENT]
)

# define updated shell command to replace existing command
@updated_shell_command = <<-UPDATED_SHELL_COMMAND
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
./build_sugar_30.php --version $version --branch $branch  --deploy --packages $package_list --upgrades $upgrade_package --author $author

rm -rf /dev/shm/sugarbuild-$version
UPDATED_SHELL_COMMAND

# makes necessary changes to config.xml in a particular job directory
def modify_config_xml(job_dir, config_path)
  config = REXML::Document.new File.new(config_path)
  project = config.elements["project"]
  # make sure this config has not already been converted
  sgr = REXML::XPath.first(config, '//name[text()="styleguide_repo"]')
  sgb = REXML::XPath.first(config, '//name[text()="styleguide_branch"]')
  scr = REXML::XPath.first(config, '//name[text()="styleguide_repo"]')
  scb = REXML::XPath.first(config, '//name[text()="styleguide_branch"]')
  if sgr or sgb or scr or scb
    puts "Skipping job because it has already been converted."
    return
  end
  puts "Converting #{job_dir}"
  # flip disableSubmodules value to true
  config.elements["/project/scm/disableSubmodules"].text = "true"
  # add parameters for styleguide and sidecar
  parameters = config.elements["/project/properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions"]
  styleguide_repo = create_job_parameter("styleguide_repo")
  styleguide_branch = create_job_parameter("styleguide_branch")
  sidecar_repo = create_job_parameter("sidecar_repo")
  sidecar_branch = create_job_parameter("sidecar_branch")
  parameters.add_element(styleguide_repo)
  parameters.add_element(styleguide_branch)
  parameters.add_element(sidecar_repo)
  parameters.add_element(sidecar_branch)
  # replace the old shell step with the new
  config.elements["/project/builders/hudson.tasks.Shell/command"].text = @updated_shell_command
  # write changes
  begin
    File.open(config_path, "w") do |data|
      data << config
    end
  rescue
    raise RuntimeError, "Failed to write converted config file at '#{config_path}'."
  end
end

# generates valid job parameter for Jenkins' config.xml file, returns REXML::Element
def create_job_parameter(name, description="", default_value="")
  parameter = REXML::Element.new("hudson.model.StringParameterDefinition")
  parameter.add_element("name").text = name
  parameter.add_element("description").text = description
  parameter.add_element("defaultValue").text = default_value
  return parameter
end

# Converts a particular jenkins job by modifying config.xml, adding styleguide and sidecar parameters
# while ensuring that <disableSubmodules> is set to true.
def convert(job_dir, backup, restore)
  config_path = "#{job_dir}/config.xml"
  backup_config_path = "#{config_path}.bak"
  if backup
    puts "Backing up job config."
    begin
      FileUtils.cp(config_path, backup_config_path)
    rescue
      raise RuntimeError, "Failed to back up file '#{config_path}' to backup location '#{backup_config_path}'."
    end
  elsif restore
    puts "Restoring backup file from '#{backup_config_path}' to original location '#{config_path}'."
    begin
      FileUtils.cp(backup_config_path, config_path)
    rescue
      raise RuntimeError, "Failed to restore backup file '#{backup_config_path}' to original location '#{config_path}'."
    end
    begin
      FileUtils.rm([backup_config_path])
    rescue
      raise RuntimeError, "Failed to remove copy of backup file after restoring to original state. Congratulations! You are now the proud new owner of a lingering backup file."
    end
    return
  end
  modify_config_xml(job_dir, config_path)
end

# initialize variables
jobs_dir = nil
pattern = nil
mock = false
backup = false
restore = false

# parse command-line options
opts.each do |opt, arg|
  case opt
    when '--help'
      RDoc::usage
      exit(1)
    when '--jobs_dir'
      if not arg
        RDoc::usage
        exit(1)
      end
      jobs_dir = arg
    when '--pattern'
      pattern = arg
    when '--mock'
      mock = true
    when '--backup'
      backup = true
    when '--restore'
      if backup
        puts "You can't back up and restore simultaneously. Please specify only --backup or --restore, not both."
        exit(1)
      end
      restore = true
  end
end

# perform sanity checks
if not jobs_dir
  RDoc::usage
end
if not File.directory?(jobs_dir)
  raise RuntimeError, "The jobs directory provided (#{jobs_dir}) does not exist or is not a directory."
end
if pattern:
  begin
    compiled_pattern = Regexp.compile(pattern)
  rescue
    raise RuntimeError, "The pattern provided (#{pattern}) could not be compiled."
  end
  pattern = compiled_pattern
end

# iterate over each jenkins job directory, process relevant job directories
Dir.foreach("#{jobs_dir}") do |item|
  next if item == '.' or item == '..'
  job_dir = "#{jobs_dir.chomp("/")}/#{item}"
  if pattern
    if item =~ pattern
      if not mock
        convert(job_dir, backup, restore)
      else
        puts "Mock converted: #{job_dir}"
      end
    end
  else
    if not mock
      convert(job_dir, backup, restore)
    else
      puts "Mock converted: #{job_dir}"
    end
  end
end
