# Running the service tests standalone

The instructions have been written with reference to the 64-bit [Ubuntu](http://www.ubuntu.com/) 14.04.2 operating system.

Other operating systems, or versions of these, may differ in how packages are installed, the versions of these packages available from package managers etc. Consult the relevant documentation for your operating system and the products concerned.

Some dependencies require you to have sudo access to install and configure software (or a local system administrator can do this for you).

This page assumes that [pyenv](https://github.com/yyuu/pyenv) is used to manage Python versions.

## Get ProvStore API key

* Log in to [ProvStore](https://provenance.ecs.soton.ac.uk/st
ore)
* Select Account => Developer Area
* You will see your API key

## Get these service tests

```
$ git clone https://github.com/prov-suite/service-tests
$ cd service-tests
$ pip install -r requirements.txt
```

## Configure test environment

Edit `setenv.sh`, replacing `user:12345qwert` with your ProvStore API key:

```
export PROVSTORE_API_KEY="user:12345qwert"
```

## Run the service tests

```
$ nosetests -v prov_service_tests
```

To run tests for a specific service:

```
$ nosetests -v prov_service_tests.test_provstore
$ nosetests -v prov_service_tests.test_provvalidator
```

If you are running on a multi-processor machine then the tests can run in parallel, using nosetests' support for [parallel testing](http://nose.readthedocs.org/en/latest/doc_tests/test_multiprocess/multiprocess.html). Specify the number of processes you want to use using a `--processes` flag e.g.

```
$ nosetests --processes=4 -v prov_service_tests
```
