# Running the service tests under Jenkins

The instructions have been written with reference to the 64-bit [Ubuntu](http://www.ubuntu.com/) 14.04.2 operating system.

Other operating systems, or versions of these, may differ in how packages are installed, the versions of these packages available from package managers etc. Consult the relevant documentation for your operating system and the products concerned.

Some dependencies require you to have sudo access to install and configure software (or a local system administrator can do this for you).

This page assumes that [pyenv](https://github.com/yyuu/pyenv) is used to manage Python versions.

## Get ProvStore API key

* Log in to [ProvStore](https://provenance.ecs.soton.ac.uk/st
ore)
* Select Account => Developer Area
* You will see your API key

## Install Jenkins

Install Java:

```
sudo apt-get -y install openjdk-7-jdk
java -version
javac -version
```

[Jenkins](https://jenkins-ci.org/) is available as an executable Java archive.  Run:

```
$ wget http://mirrors.jenkins-ci.org/war/latest/jenkins.war
```

To start Jenkins, run:

```
$ java -jar jenkins.war
```

* Open a web browser and go to to http://localhost:8080

## Install workspace cleanup plugin

Jenkins uses a "workspace" directory to store any build artefacts. This plugin allows jobs to be configured to clear this directory between build runs.

* Click Manage Jenkins
* Click Manage Plugins
* Click Available tab
* Filter: workspace cleanup
* Check Workspace Cleanup Plugin
* Click Install without restart
* Click go back to top page

## Create job to run service tests

These steps create a Jenkins job to run the service tests. If you do not want to execute these manually, there is one we have prepared earlier in [config-services.xml](./jenkins/config-services.xml) - to use this see "Importing a Jenkins job" below.

* Click create new jobs
* Item name: PTS-Services
* Select freestyle project
* Click OK

Set build configuration:

* Source Code Management: None (for now)
* Build Triggers: leave unchecked (for now)
* Check Build Environment Delete workspace before build starts

Add step to set Python version:

* Select Add build step => Execute shell
* Enter:

```
pyenv local 2.7.6
```

* If you want to run using Python 3.4.0 then change `2.7.6` to `3.4.0`

Add step to get service tests:

* Select Add build step => Execute shell
* Enter:

```
git clone https://github.com/prov-suite/service-tests
cd service-tests
pip install -r requirements.txt
```

Add step to run all service tests:


* Select Add build step => Execute shell
* Enter the following, replacing `user:12345qwert` with your ProvStore API key:

```
cd service-tests
export PROVVALIDATOR_URL=https://provenance.ecs.soton.ac.uk/validator/provapi/documents/
export PROVSTORE_URL=https://provenance.ecs.soton.ac.uk/store/api/v0/documents/
export PROVSTORE_API_KEY="user:12345qwert"
nosetests -v --with-xunit prov_service_tests
```

* Click Save
* Project PTS-Services page appears
* Click Build Now
* Click #NNNN build number
* Build #NNNN page appears
* Click Console Output

The Execute shell steps can, alternatively, be done within a single Execute shell entry.

If you are only interested in running tests for a specific service then use the relevant line from:

```
nosetests -v --with-xunit prov_service_tests.test_provstore
nosetests -v --with-xunit prov_service_tests.test_provvalidator
```

## Publish xUnit test results

nosetests, with the ``--with-xunit`` option set, outputs test results in xUnit-compliant XML. By default, this file is called nosetests.xml. Jenkins can parse and present this informationy.

* Go to Project PTS-Services page
* Click Configure
* Scroll down to Post-build Action
* Select Add post-build action => Publish JUnit test result report
* Test report XMLs: test-harness/nosetests.xml
  - If you get a warning that nosetests.xml doesn't match anything you can ignore this as the file hasn't been created yet
* Click Save
* Click Build Now
* Click #NNNN build number
* Build #NNNN page appears

## View nosetests test results

You can browse the nosetests test results. These are hierarchically organised by Python module, class and method name.

* EITHER On the Project PTS-Services page
  - Click the Latest Test Result link
  - If all went well, should say (no failures)
* OR On the Jenkins dashboard/front-page
  - Hover over the build number #NNNN
  - Click drop-down arrow
  - Select Test Result
* Click Python package names to browse down to test classes
* Click Python class names to browse down to test functions

## Start builds manually

* EITHER On the Project PTS-Services page
  - Click Build Now
* OR On the Jenkins dashboard/front-page
  - Click green "run" icon
* Click #NNNN build number
* Build #NNNN page appears
* Click Console Output to see commands being run by Jenkins

## Importing a Jenkins job

[config-services.xml](./jenkins/config-services.xml) contains the Jenkins configuration file for the job written following the above instructions. Assuming you have already done:

* Install dependencies
* Get ProvStore API key
* Install Jenkins
* Install workspace cleanup plugin

Edit jenkins/config-services.xml and in the line:

```
export PROVSTORE_API_KEY=&quot;user:12345qwert&quot;
```

replace `user:12345qwert` with your ProvStore username and API key.

Import configuration into Jenkins:

```
$ mkdir $HOME/.jenkins/jobs/PTS-Services/
$ cp jenkins/config-services.xml $HOME/.jenkins/jobs/PTS-Services/config.xml
```

On the Jenkins dashboard:

* Click Manage Jenkins
* Click Reload configuration from disk
* You should see PTS-Services
* Click green "run" icon

## Jenkins directories

Jenkins stores its files in `$HOME/.jenkins`.

Jenkins does the build in job-specific workspace directory, `.jenkins/workspace/JOB`, e.g. `.jenkins/workspace/PTS-Services/`.

Jenkins job configuration, ``config.xml``, and logs and xUnit test results from all the builds, and the previous workspace, are stored in a job-specific jobs directory, `.jenkins/jobs/JOB`, e.g. `.jenkins/jobs/PTS-Services/`.
