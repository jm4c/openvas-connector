# OpenVAS Connector

OpenVAS Connector is a Python module used to manage OpenVAS Servers using the [OpenVAS Management Protocol (OMP) 7.0](https://docs.greenbone.net/API/OMP/omp-7.0.html)  through the OpenVAS Command Line Interface
(OpenVAS-CLI). It was implemented as part of my thesis because the official OpenVAS
Python module (openvas.omplib) was not compatible with most recent versions of the OMP
nor with Python 3 and I could not find better alternatives at the time.

Not all OMP features are implemented in the module for now as this Python library was
meant to be used as a tool for this dissertation in the first place, however it should be easily
extendable. The current version of the OpenVAS Connector allows the user to:

- Create new alerts, targets or tasks;
- Get alerts, configurations, port lists, reports, results, tasks or targets. The `get` methods
can use a filter to obtain only specific objects or no filters to get all available, e.g.
`get_target()` returns all available targets while `get_target(filter=’name="SmallCo Network"’)` only returns the target named “SmallCo Network”;
- Get a delta report of the two last reports generated, if only one report exists it returns
it. A delta report is a report based on the difference between two reports of the same
task. With a delta report it is possible to determine which results are new, modified,
the same or gone. This is used by the script to avoid duplicated events from the same
result.
- Lock the execution of the current thread until a previously defined alert in OpenVAS
is fired by a task. This is used by the script to wait for the OpenVAS scan to finish.

## Getting Started

To use this module:
- All the prequisites must be installed;
- The file `openvas_connector.py` must be in the project directory;
- A configuration file of OMP must be created (`~/omp.config`).

### Prerequisites
- OpenVAS Scanner 4.0 (or higher)
- OMP 7.0 
- Python 3.4 (or higher)
- LXML
```
pip install lxml
```

### Configuration file of OMP

The configuration file `~/omp.config` is used to store connection parameter like host, port, username and password.

An exemplary configuration file looks like
```
[Connection]
host=localhost
port=9390
username=exampleuser
password=examplepassword
```

## References
- [OpenVAS](http://www.openvas.org/)
- [OpenVAS Scanner](https://github.com/greenbone/openvas-scanner)
- [OpenVAS Management Protocol (OMP) 7.0](https://docs.greenbone.net/API/OMP/omp-7.0.html)
- [OpenVAS CLI](http://www.openvas.org/src-doc/openvas-cli/index.html)
- [LXML](https://lxml.de/)

## Contributing

Feel free to contribute and add yourself to the Authors section. All commits to the master branch are reviewed before approval. There is currently no automated testing in place and I am not actively contributing so approvals might take a while. 

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **João Machado** - *Initial work* - [jm4c](https://github.com/jm4c)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
