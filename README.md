# INTO CPS DSE Scripts

[INTO-CPS](https://into-cps.org/) DSE scripts updated from Python 2 to Python 3 and with added modular GA system for DSE

## Highlights
- Updated to Python 3
- Powerful command line arguements
- Added multi threading to allow for multiple parallel simulations
- Added modular GA system
- FMU parameter names {fmu}.dummy.ab will no longer be incorrectly matched with {fmu}.dummy.a for constraints

## Dependancies
- Python 3
- Numpy
- Matplotlib
- Maestro Web Api (COE) Version 1.0.10

## Known Issues
  - Numpy 1.19.4, Python 3.9, and Windows do not play nice

## Usage

```console
python Algorithm_selector.py C:\INTOProjects\TestProject\ DSEs\new-dse\new-dse.dse.json Multi-models\mm-new\co-sim\coe.json
```

Where folder structure is:
```
C:
└── INTOProjects
    └── TestProject
        ├── DSEs
        │   └── new-dse
        │       └── new-dse.dse.json
        ├── FMUs
        │   └── (FMUs to run)
        ├── Multi-models
        │   └── mm-new
        │       └── co-sim
        │           └── coe.json
        └── userMetricScripts (optional)
```

Results will be placed in the folder beloning to the dse being run (see below) in a folder named by the date and time the dse was started
```
C:
└── INTOProjects
    └── TestProject
        └── DSEs
            └── new-dse
                └── <results>
```

## Command Line Arguments

(Arguments apply to Algroithm Selector, Exhaustive, and Genetic)

- `help`
- `t` Number of threads to use, default 1
- `noCSV` do not generate CSV result file, default false
- `noHTML` do not generate HTML result file, default false
- `u` URL to COE, default http://localhost
- `p` Port for COE, default 8082

## DSE Config for GA's

Please see wiki
