# Service Tests

Service tests for the [Southampton Provenance Suite](https://provenance.ecs.soton.ac.uk) services:

* [ProvValidator and ProvTranslator](https://provenance.ecs.soton.ac.uk/validator)
* [ProvStore](https://provenance.ecs.soton.ac.uk/store/)

These tests check that the services are available and respond to requests directed against their REST APIs.

The tests run under Python 2.7+ and Python 3.

[![Build Status](https://travis-ci.org/prov-suite/service-tests.svg)](https://travis-ci.org/prov-suite/service-tests)

## ProvStore tests and API keys

Running ProvStore tests require you to create a ProvStore API Key:

* Log in to [ProvStore](https://provenance.ecs.soton.ac.uk/store)
* Select Account => Developer Area
* You will see your API key

## Running under Travis CI

The tests can be run under [Travis CI](https://travis-ci.org). This respository contains a TravisCI, .travis.yml, job configuration file.

Running the service tests under Travis CI require you to:

* Create a ProvStore API Key:
  - Log in to [ProvStore](https://provenance.ecs.soton.ac.uk/store)
  - Select Account => Developer Area
  - You will see your API key
* Define a Travis CI variable, `PROVSTORE_API_KEY` holding your ProvStore user name and API key:
  - Visit your job's settings page in Travis CI
  - Select settings
  - Click Environment Variables
  - Click Add a new variable
  - Name: `PROVSTORE_API_KEY`
  - Value: `user:qwert12345`
  - Ensure Display value in build logs is *not* selected  
  - See [define variables in repository settings](http://docs.travis-ci.com/user/environment-variables/#Defining-Variables-in-Repository-Settings).

## Running under Jenkins

[Jenkins](https://jenkins-ci.org) is a popular, open source continuous integration server that runs under Java.

See [Running the service tests under Jenkins](./Jenkins.md) which includes an example of a Jenkins job to run the tests.

## Running standalone

The service tests can be run stand-alone. See [Running the service tests standalone](./Standalone.md).

## Author

Developed by [The Software Sustainability Institute](http://www.software.ac.uk>) and the [Provenance Tool Suite](http://provenance.ecs.soton.ac.uk/) team at [Electronics and Computer Science](http://www.ecs.soton.ac.uk) at the [University of Southampton](http://www.soton.ac.uk).

For more information, see our [document repository](https://github.com/prov-suite/ssi-consultancy/).

## License

The code is released under the MIT license.
