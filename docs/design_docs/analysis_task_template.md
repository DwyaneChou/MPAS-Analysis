Analysis Task Template
======================

<h2>
Xylar Asay-Davis <br>
date: 2017/03/08 <br>
</h2>
<h3> Summary </h3>

A new template python file for analysis tasks will be added to the repository.
The template will include a list of functions that each analysis task *must*
implement and example syntax for docstrings used to commend both the full
analysis task and the individual functions.

The existing analysis tasks will be updated to be consistent with this template.
The `run_analysis.py` driver script will also be updated to work with the template.

The template is needed to:
1. serve as a starting point for writing new analysis tasks
2. ensure that tasks implement a standard set of
   functions, making it easier to perform actions (such as checking whether
   the task should be run, checking for required model and observations files,
   purging files from a previous analysis run, and running the analysis) on
   each analysis task in sequence (and, in the future, in parallel)
3. demonstrate the syntax and style of docstrings required to comment/document
   each task and each function

<h3> Requirements </h3>

<h4> Requirement: Template for Analysis Tasks <br>
Date last modified: 2017/03/08 <br>
Contributors: Xylar Asay-Davis
</h4>

The template should include each function that each analysis task *must* implement
and example docstring both for the task as a whole and for each funciton.

<h4> Requirement: Validation within Analysis Tasks <br>
Date last modified: 2017/03/08 <br>
Contributors: Xylar Asay-Davis
</h4>

Validation, such as checking config options or adding new ones if they are missing,
or checking if required data files are present, should be performed within a
function in each task (rather than in `run_analysis.py`, as is sometimes the current
case).

<h4> Requirement: Analysis Continues even when Analysis Task Fails <br>
Date last modified: 2017/03/08 <br>
Contributors: Xylar Asay-Davis
</h4>

If validation fails, an error message should be printed but other analysis
tasks should be allowed to run.  Similarly, if a given analysis task raises
an exception, the error and stack trace should be printed but other analysis
tasks should still be run.

<h4> Requirement: List of Tasks to Perform<br>
Date last modified: 2017/03/16 <br>
Contributors: Xylar Asay-Davis
</h4>

There should be a single place where new tasks are added to `run_analysis.py`, as
is presently the case.  Yet, there should be a way to create a list of tasks to be
performed and later determine whether, when and how those tasks are to be run.
This capability also allows for operations like purging files from a prevous run
to be added in the future. The capability is also requried to allow for later task
parallelism. Currently, a task module is imported, there is a check to see if that
task should be run, and the task is performed in immediate sequence.

<h3> Algorithmic Formulations (optional) </h3>

<h4> Design solution: Template for Analysis Tasks <br>
Date last modified: 2017/03/16 <br>
Contributors: Xylar Asay-Davis
</h4>

A base class, `AnalysisTask` will be added under `shared/analysis_task.py`.
This class will include methods:
  * `__init__`: construct the task, including assigning variable and streams maps
    (optional).
  * `setup_and_check`: performs common tasks to all analysis, such as reading
     namelist and streams files
  * `run`: the base class version does nothing

The template will show how to set up a child class that decends from `AnalysisTask`.
It will show examples of:
  * `__init__`: construct the task, including assigning the `taskName`, `componentName`
     and `categories` of the analysis, and calling the base class's constructor.
  * `setup_and_check`: first, calls the base class' version of `setup_and_check`, then,
     determines if the configuration is valid for running this task (e.g. if
     necessary files and config options are present)
  * `run`: runs the analysis task

The template will be located at:
```
mpas_analysis/
    - analysis_task_template.py
```
That is, it is the only file (other than `__init__.py`) in the base of the
`mpas_analysis` directory, making it easy to find.  This way, it will be the first
file most developers see when they look in `mpas_analysis` itself.

A reference to the template as the starting point for new developers will be added
to the readme.

<h4> Design solution: Validation within Analysis Tasks <br>
Date last modified: 2017/03/16 <br>
Contributors: Xylar Asay-Davis
</h4>

The `setup_and_check` method within each analysis task can be used to determine if
necessary input files are present and/or if config options are set as expected.
The template will provide examples of doing this.

Existing checks for missing observations files in `run_analysis.py` will be
moved to individual analyses.  This will make clearer which checks correspond
with which analysis tasks and will make clearer where such checks should be added
within future analysis tasks.  Similarly, the addition of the `startDate` and
`endDate` config options will be moved to the corresponding analysis tasks.

<h4> Design solution: Analysis Continues even when Analysis Task Fails <br>
Date last modified: 2017/03/08 <br>
Contributors: Xylar Asay-Davis
</h4>

A try/except will be used around both `setup_and_check` and `run` calls to make sure
an error message and stack trace are printed, but execution will continue
for other tasks.

<h4> Design solution: List of Tasks to Perform<br>
Date last modified: 2017/03/16 <br>
Contributors: Xylar Asay-Davis
</h4>

By having a common base class for all analysis tasks,
each task can be checked to see if it should be run based on
the `generate` command-line or config option.  If so, its `setup_and_check`
function will be run to make sure the configuration is right (and will
print a warning if not).  If `setup_and_check` passes, the analysis can be added
to a list of functions to be run.  Later, a loop through the list
can be used to run each analysis.

Some analysis tasks require extra arguments (e.g. the field to be
analyzed in the case of `ocean.modelvsobs` and the streams and variable
maps for all analysis tasks).  These arguments will be passed to `__init__`
and stored as member variables that can later be accessed via `self.<varName>`.


<h3> Design and Implementation </h3>

Implementation is in the branch: https://github.com/xylar/MPAS-Analysis/tree/analysis_task_template

<h4> Implementation: Template for Analysis Tasks <br>
Date last modified: 2017/03/16 <br>
Contributors: Xylar Asay-Davis
</h4>

Here is the suggested base class `AnalysisTask` in full, intended to make discussion
of individual lines easier:

```python
"""
Defines the base class for analysis tasks.

Authors
-------
Xylar Asay-Davis

Last Modified
-------------
03/16/2017
"""

from ..shared.io import NameList, StreamsFile
from ..shared.io.utility import build_config_full_path, make_directories


class AnalysisTask(object):  # {{{
    """
    The base class for analysis tasks.

    Authors
    -------
    Xylar Asay-Davis

    Last Modified
    -------------
    03/16/2017
    """
    def __init__(self, config, streamMap=None, variableMap=None):  # {{{
        """
        Construct the analysis task.

        Individual tasks (children classes of this base class) should first
        call this method to perform basic initialization, then, define the
        `taskName`, `componentName` and list of `categories` for the task.

        Parameters
        ----------
        config :  instance of MpasAnalysisConfigParser
            Contains configuration options

        streamMap : dict, optional
            A dictionary of MPAS-O stream names that map to their mpas_analysis
            counterparts.

        variableMap : dict, optional
            A dictionary of MPAS-O variable names that map to their
            mpas_analysis counterparts.

        Authors
        -------
        Xylar Asay-Davis

        Last Modified
        -------------
        03/16/2017
        """
        self.config = config
        self.streamMap = streamMap
        self.variableMap = variableMap  # }}}

    def setup_and_check(self):  # {{{
        """
        Perform steps to set up the analysis (e.g. reading namelists and
        streams files).

        After this call, the following member variables are set:
            self.inDirectory : the base input directory
            self.plotsDirectory : the directory for writing plots (which is
                also created if it doesn't exist)
            self.namelist : the namelist reader
            self.streams : the streams file reader
            self.calendar : the name of the calendar ('gregorian' or
                'gregoraian_noleap')

        Individual tasks (children classes of this base class) should first
        call this method to perform basic setup, then, check whether the
        configuration is correct for a given analysis and perform additional,
        analysis-specific setup.  For example, this function could check if
        necessary observations and other data files are found, then, determine
        the list of files to be read when the analysis is run.

        Authors
        -------
        Xylar Asay-Davis

        Last Modified
        -------------
        03/16/2017
        """
        # read parameters from config file
        self.inDirectory = self.config.get('input', 'baseDirectory')
        self.plotsDirectory = build_config_full_path(self.config, 'output',
                                                     'plotsSubdirectory')
        namelistFileName = self.config.get('input', 'oceanNamelistFileName')
        self.namelist = NameList(namelistFileName, path=self.inDirectory)

        streamsFileName = self.config.get('input', 'oceanStreamsFileName')
        self.streams = StreamsFile(streamsFileName,
                                   streamsdir=self.inDirectory)

        self.calendar = self.namelist.get('config_calendar_type')

        make_directories(self.plotsDirectory)
        # }}}

    def run(self):  # {{{
        """
        Runs the analysis task.

        Individual tasks (children classes of this base class) should first
        call this method to perform any common steps in an analysis task,
        then, perform the steps required to run the analysis task.

        Authors
        -------
        Xylar Asay-Davis

        Last Modified
        -------------
        03/16/2017
        """
        return  # }}}

    def check_generate(self):
        # {{{
        """
        Determines if this analysis should be generated, based on the
        `generate` config option and `taskName`, `componentName` and
        `categories`.

        Individual tasks do not need to create their own versions of this
        function.

        Returns
        -------
        generate : bool
            Whether or not this task should be run.

        Raises
        ------
        ValueError : If one of `self.taskName`, `self.componentName`
            or `self.categories` has not been set.

        Authors
        -------
        Xylar Asay-Davis

        Last Modified
        -------------
        03/16/2017s
        """

        for memberName in ['taskName', 'componentName', 'categories']:
            if not hasattr(self, memberName):
                raise ValueError('Analysis tasks must define self.{} in their '
                                 '__init__ method.'.format(memberName))

        if (not isinstance(self.categories, list) and
                self.categories is not None):
            raise ValueError('Analysis tasks\'s member self.categories '
                             'must be NOne or a list of strings.')

        config = self.config
        generateList = config.getExpression('output', 'generate')
        generate = False
        for element in generateList:
            if '_' in element:
                (prefix, suffix) = element.split('_', 1)
            else:
                prefix = element
                suffix = None

            allSuffixes = [self.componentName]
            if self.categories is not None:
                allSuffixes = allSuffixes + self.categories
            noSuffixes = [self.taskName] + allSuffixes
            if prefix == 'all':
                if (suffix in allSuffixes) or (suffix is None):
                    generate = True
            elif prefix == 'no':
                if suffix in noSuffixes:
                    generate = False
            elif element == self.taskName:
                generate = True

        return generate  # }}}
# }}}

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
```

And here is the suggested template in full:

```python
"""
This is an example analysis task to be used as a template for new tasks.
It should be copied into one of the component folders (`ocean`, `sea_ice`,
`land_ice`, etc.) and modified as needed.

Don't forget to remove this docstring. (It's not needed.)

Authors
-------
Xylar Asay-Davis

Last Modified
-------------
03/16/2017
"""

# import python modules here

# import mpas_analysis module here (those with relative paths starting with
# dots)
from ..shared.analysis_task import AnalysisTask


class MyTask(AnalysisTask):  # {{{
    """
    <Describe the analysis task here.>

    Authors
    -------
    <List of authors>

    Last Modified
    -------------
    <MM/DD/YYYY>
    """
    def __init__(self, config, streamMap=None, variableMap=None,
                 myArg='myDefaultValue'):  # {{{
        """
        Construct the analysis task.

        Parameters
        ----------
        config :  instance of MpasAnalysisConfigParser
            Contains configuration options

        streamMap : dict, optional
            A dictionary of MPAS-O stream names that map to their mpas_analysis
            counterparts.

        variableMap : dict, optional
            A dictionary of MPAS-O variable names that map to their
            mpas_analysis counterparts.

        myNewArg : str, optional
            <Describe the arg>

        Authors
        -------
        <List of authors>

        Last Modified
        -------------
        <MM/DD/YYYY>
        """
        # first, call the constructor from the base class (AnalysisTask)
        super(MyTask, self).__init__(config, streamMap, variableMap).__init__(config, streamMap, variableMap)

        # next, name the task, the component (ocean, sea_ice, etc.) and the
        # categories (if any) of the component ('timeSeries', 'climatologyMap'
        # etc.)
        self.taskName = 'myTask'
        self.componentName = 'component'
        self.categories = ['category1', 'category2']

        # then, store any additional arguments for use later on.  These would
        # likely include things like the name of a field, region, month,
        # season, etc. to be analyzed so that the same subclass of AnalysisTask
        # can perform several different tasks (potentially in parallel)
        self.myArg = myArg
        # }}}

    def setup_and_check(self):  # {{{
        """
        Perform steps to set up the analysis and check for errors in the setup.

        Raises
        ------
        ValueError: if myArg has an invalid value

        Authors
        -------
        <List of authors>

        Last Modified
        -------------
        <MM/DD/YYYY>
        """

        # first, call setup_and_check from the base class (AnalysisTask),
        # which will perform some common setup, including storing:
        #   self.inDirectory, self.plotsDirectory, self.namelist, self.streams
        #   self.calendar
        super(MyTask, self).__init__(config, streamMap, variableMap).setup_and_check()

        # then, perform additional checks specific to this analysis
        possibleArgs = ['blah', 'thing', 'stuff']
        if self.myArg not in possibleArgs:
            # Note: we're going to allow a long line in this case because it
            # would be confusing to break up the string (even though it
            # violates the PEP8 standard)
            raise ValueError('MyTask must be constructed with argument myArg having one of the values\n'
                             '{}.'.format(possibleArgs))

        section = 'MyTask'
        startDate = '{:04d}-01-01_00:00:00'.format(
            self.config.getint(section, 'startYear'))
        if not self.config.has_option(section, 'startDate'):
            self.config.set(section, 'startDate', startDate)
        endDate = '{:04d}-12-31_23:59:59'.format(
            self.config.getint(section, 'endYear'))
        if not self.config.has_option(section, 'endDate'):
            self.config.set(section, 'endDate', endDate)

        # }}}

    def run(self):  # {{{
        """
        Runs the analysis task.

        Individual tasks (children classes of this base class) should first
        call this method to perform any common steps in an analysis task,
        then, perform the steps required to run the analysis task.

        Authors
        -------
        <List of authors>

        Last Modified
        -------------
        <MM/DD/YYYY>
        """

        # here is where the main "meat" of the analysis task goes

        self._my_sub_task('someText', arg2='differentText')
        return
        # }}}

    # here is where you add helper methods that are meant to be non-public
    # (they start with an underscore), meaning you don't expect anyone to
    # access them outside of this file.  Typically you won't put as much in
    # the docstring as you would for a public function or method.
    #
    # you can either pass arguments (with or without defaults) or you can
    # "save" arguments as member variables of `self` and then get them back
    # (like `self.myArg` here).
    def _my_sub_task(self, arg1, arg2=None):  # {{{
        """
        <Performs my favority subtask>
        """

        # perform the task
        print 'myArg:', self.myArg
        print 'arg1:', arg1
        if arg2 is not None:
            print 'arg2:', arg2
        # }}}

# }}}

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
```

<h4> Implementation: Validation within Analysis Tasks <br>
Date last modified: 2017/03/08 <br>
Contributors: Xylar Asay-Davis
</h4>

Here is an example (from `ocean.climatology_map.ClimatologyMap`) of what
the new `__init__` and `setup_and_check` methods :
```python
def __init__(self, config, streamMap=None, variableMap=None,
             fieldName=None):  # {{{
    """
    Construct the analysis task.

    Parameters
    ----------
    config :  instance of MpasAnalysisConfigParser
        Contains configuration options

    streamMap : dict, optional
        A dictionary of MPAS-O stream names that map to their mpas_analysis
        counterparts.

    variableMap : dict, optional
        A dictionary of MPAS-O variable names that map to their
        mpas_analysis counterparts.

    fieldName : {'sst', 'mld', 'sss'}
        The name of the field to be analyzed

    Raises
    ------
    ValueError : if `fieldName` is not provided or is not one of the
        supported values

    Authors
    -------
    Xylar Asay-Davis

    Last Modified
    -------------
    03/16/2017
    """
    # first, call the constructor from the base class (AnalysisTask)
    AnalysisTask.__init__(config, streamMap, variableMap)

    upperFieldNames = {'sst': 'SST',
                       'mld': 'MLD',
                       'sss': 'SSS'
                       # 'nino34': 'Nino34',
                       # 'mht': 'MHT'
                       # 'moc': 'MOC'
                       }

    if fieldName is None:
        raise ValueError('fieldName must be supplied.')
    if fieldName not in upperFieldNames.keys():
        raise ValueError('fieldName must be one of {}.'.format(
            upperFieldNames.keys()))

    self.fieldName = fieldName
    self.upperFieldName = upperFieldNames[fieldName]

    # name the task, component and category
    self.taskName = 'climatologyMap{}'.format(self.upperFieldName)
    self.componentName = 'ocean'
    self.categories = ['climatologyMap', fieldName]

    # }}}

def setup_and_check(self):  # {{{
    """
    Perform steps to set up the analysis and check for errors in the setup.

    Raises
    ------
    OSError
        If files are not present

    Authors
    -------
    Xylar Asay-Davis

    Last Modified
    -------------
    03/16/2017
    """
    config = self.config
    section = 'climatology'
    startDate = '{:04d}-01-01_00:00:00'.format(
        config.getint(section, 'startYear'))
    if not config.has_option(section, 'startDate'):
        config.set(section, 'startDate', startDate)
    endDate = '{:04d}-12-31_23:59:59'.format(
        config.getint(section, 'endYear'))
    if not config.has_option(section, 'endDate'):
        config.set(section, 'endDate', endDate)

    return  # }}}
```
Much of this code has been taken out of `run_analysis.py`, simplifying and clarifying
the code.

<h4> Implementation: Analysis Continues even when Analysis Task Fails <br>
Date last modified: 2017/03/16 <br>
Contributors: Xylar Asay-Davis
</h4>

Calls to `check` and `run` methods in `run_analysis.py` are inside of
`try/except` blocks, which catch the exceptions and print the stack trace
but don't cause the code to exit.
```python
try:
    analysisTask.check()
...
except:
    traceback.print_exc(file=sys.stdout)
    print "ERROR: analysis module {} failed during check and " \
        "will not be run".format(analysisTask.taskName)

...

try:
    analysisModule.run()
except:
    traceback.print_exc(file=sys.stdout)
    print "ERROR: analysis module {} failed during run".format(
        analysisTask.taskName)
```

<h4> Implementation: List of Tasks to Perform<br>
Date last modified: 2017/03/16 <br>
Contributors: Xylar Asay-Davis
</h4>

The tasks are imported and added to an anaysis list as follows:
```python
analyses = []

# Ocean Analyses
from mpas_analysis.ocean.time_series_ohc import TimeSeriesOHC
analyses.append(TimeSeriesOHC(config, streamMap=oceanStreamMap,
                              variableMap=oceanVariableMap))
from mpas_analysis.ocean.time_series_sst import TimeSeriesSST
analyses.append(TimeSeriesSST(config, streamMap=oceanStreamMap,
                              variableMap=oceanVariableMap))

from mpas_analysis.ocean.climatology_map import ClimatologyMap \
    as ClimatologyMapOcean
for fieldName in ['sst', 'mld', 'sss']:
    analyses.append(ClimatologyMapOcean(config, streamMap=oceanStreamMap,
                                        variableMap=oceanVariableMap,
                                        fieldName=fieldName))

# Sea Ice Analyses
from mpas_analysis.sea_ice.timeseries import TimeSeries as TimeSeriesSeaIce
analyses.append(TimeSeriesSeaIce(config, streamMap=seaIceStreamMap,
                                 variableMap=seaIceVariableMap))
from mpas_analysis.sea_ice.climatology_map import ClimatologyMap \
    as ClimatologyMapSeaIce
analyses.append(ClimatologyMapSeaIce(config, streamMap=seaIceStreamMap,
                                     variableMap=seaIceVariableMap))
```
The `analyses` list is a list of instances of subclasses of `AnalysisTask`.

Subsequent calls to analysis functions can loop over analyses, as in the following
example for calling `run`:
```python
# run each analysis task
for analysisTask in analyses:
    try:
        analysisTask.run()
    except:
        traceback.print_exc(file=sys.stdout)
        print "ERROR: analysis module {} failed during run".format(
            analysisTask.taskName)
```

<h3> Testing </h3>
<h4> Testing and Validation: Template for Analysis Tasks <br>
Date last modified: 2017/03/10 <br>
Contributors: Xylar Asay-Davis
</h4>

Ideally, the test here would be having another developer create an analysis task based on this
template.  Realistically, this won't happen before the template gets merged into the repository,
so I'm counting on feedback from other developers to "test" the template before it gets merged,
and there will probably need to be subsequent PRs to make changes as issues arise.

<h4> Testing and Validation: Validation within Analysis Tasks <br>
Date last modified: 2017/03/16 <br>
Contributors: Xylar Asay-Davis
</h4>

I have added `setup_and_check` functions within each analysis task.  So far, these check for only a subset of
the necessary configuration and input files, and could (and should) be expanded in the future.

I have verified that all `setup_and_check` routines fail when the path to their respective observations and/or
preprocessed reference run is not found.

<h4> Testing and Validation: Analysis Continues even when Analysis Task Fails <br>
Date last modified: 2017/03/10 <br>
Contributors: Xylar Asay-Davis
</h4>

I have verified using the `GMPAS_QU240` test case and by deliberately introducing errors in the file
paths that an error in a given analysis task (either during `setup_and_check` or `run`) causes that task to
print a stack trace and an error message but does not prevent other tasks from running.

<h4> Testing and Validation: List of Tasks to Perform<br>
Date last modified: 2017/03/10 <br>
Contributors: Xylar Asay-Davis
</h4>

As stated in implementation, there is a single place in `run_analysis.py` where a developer would add
her or his task to the analysis.  I think this requirement has been satisfied without requiring testing.
