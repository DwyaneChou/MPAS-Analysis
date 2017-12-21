from __future__ import absolute_import, division, print_function, \
    unicode_literals

import xarray as xr
import datetime

from ..shared import AnalysisTask

from ..shared.io.utility import build_config_full_path

from ..shared.climatology import RemapMpasClimatologySubtask, \
    RemapObservedClimatologySubtask

from .plot_climatology_map_subtask import PlotClimatologyMapSubtask

from ..shared.grid import LatLonGridDescriptor


class ClimatologyMapSST(AnalysisTask):  # {{{
    """
    An analysis task for comparison of sea surface temperature (sst) against
    observations

    Authors
    -------
    Luke Van Roekel, Xylar Asay-Davis, Milena Veneziani
    """
    def __init__(self, config, mpasClimatologyTask):  # {{{
        """
        Construct the analysis task.

        Parameters
        ----------
        config :  instance of MpasAnalysisConfigParser
            Contains configuration options

        mpasClimatologyTask : ``MpasClimatologyTask``
            The task that produced the climatology to be remapped and plotted

        Authors
        -------
        Xylar Asay-Davis
        """
        self.fieldName = 'sst'
        # call the constructor from the base class (AnalysisTask)
        super(ClimatologyMapSST, self).__init__(
                config=config, taskName='climatologyMapSST',
                componentName='ocean',
                tags=['climatology', 'horizontalMap', self.fieldName])

        mpasFieldName = 'timeMonthly_avg_activeTracers_temperature'
        iselValues = {'nVertLevels': 0}

        sectionName = self.taskName

        climStartYear = config.getint('oceanObservations',
                                      'sstClimatologyStartYear')
        climEndYear = config.getint('oceanObservations',
                                    'sstClimatologyEndYear')

        if climStartYear < 1925:
            period = 'pre-industrial'
        else:
            period = 'present-day'

        observationTitleLabel = \
            'Observations (Hadley/OI, {} {:04d}-{:04d})'.format(period,
                                                                climStartYear,
                                                                climEndYear)

        observationsDirectory = build_config_full_path(
            config, 'oceanObservations',
            '{}Subdirectory'.format(self.fieldName))

        obsFileName = \
            "{}/MODEL.SST.HAD187001-198110.OI198111-201203.nc".format(
                observationsDirectory)
        obsFieldName = 'sst'

        # read in what seasons we want to plot
        seasons = config.getExpression(sectionName, 'seasons')

        if len(seasons) == 0:
            raise ValueError('config section {} does not contain valid list '
                             'of seasons'.format(sectionName))

        comparisonGridNames = config.getExpression(sectionName,
                                                   'comparisonGrids')

        if len(comparisonGridNames) == 0:
            raise ValueError('config section {} does not contain valid list '
                             'of comparison grids'.format(sectionName))

        # the variable self.mpasFieldName will be added to mpasClimatologyTask
        # along with the seasons.
        remapClimatologySubtask = RemapMpasClimatologySubtask(
            mpasClimatologyTask=mpasClimatologyTask,
            parentTask=self,
            climatologyName=self.fieldName,
            variableList=[mpasFieldName],
            comparisonGridNames=comparisonGridNames,
            seasons=seasons,
            iselValues=iselValues)

        remapObservationsSubtask = RemapObservedSSTClimatology(
                parentTask=self, seasons=seasons, fileName=obsFileName,
                outFilePrefix=obsFieldName,
                comparisonGridNames=comparisonGridNames)
        self.add_subtask(remapObservationsSubtask)
        for comparisonGridName in comparisonGridNames:
            for season in seasons:
                # make a new subtask for this season and comparison grid
                subtask = PlotClimatologyMapSubtask(self, season,
                                                    comparisonGridName,
                                                    remapClimatologySubtask,
                                                    remapObservationsSubtask)

                subtask.set_plot_info(
                        outFileLabel='sstHADOI',
                        fieldNameInTitle='SST',
                        mpasFieldName=mpasFieldName,
                        obsFieldName=obsFieldName,
                        observationTitleLabel=observationTitleLabel,
                        unitsLabel=r'$^o$C',
                        imageCaption='Mean Sea Surface Temperature',
                        galleryGroup='Sea Surface Temperature',
                        groupSubtitle=None,
                        groupLink='sst',
                        galleryName='Observations: Hadley-NOAA-OI')

                self.add_subtask(subtask)
        # }}}
    # }}}


class RemapObservedSSTClimatology(RemapObservedClimatologySubtask):  # {{{
    """
    A subtask for reading and remapping SST observations

    Authors
    -------
    Luke Van Roekel, Xylar Asay-Davis, Milena Veneziani
    """

    def get_observation_descriptor(self, fileName):  # {{{
        '''
        get a MeshDescriptor for the observation grid

        Parameters
        ----------
        fileName : str
            observation file name describing the source grid

        Returns
        -------
        obsDescriptor : ``MeshDescriptor``
            The descriptor for the observation grid

        Authors
        -------
        Xylar Asay-Davis
        '''

        # create a descriptor of the observation grid using the lat/lon
        # coordinates
        obsDescriptor = LatLonGridDescriptor.read(fileName=fileName,
                                                  latVarName='lat',
                                                  lonVarName='lon')
        return obsDescriptor  # }}}

    def build_observational_dataset(self, fileName):  # {{{
        '''
        read in the data sets for observations, and possibly rename some
        variables and dimensions

        Parameters
        ----------
        fileName : str
            observation file name

        Returns
        -------
        dsObs : ``xarray.Dataset``
            The observational dataset

        Authors
        -------
        Xylar Asay-Davis
        '''

        climStartYear = self.config.getint('oceanObservations',
                                           'sstClimatologyStartYear')
        climEndYear = self.config.getint('oceanObservations',
                                         'sstClimatologyEndYear')
        timeStart = datetime.datetime(year=climStartYear, month=1, day=1)
        timeEnd = datetime.datetime(year=climEndYear, month=12, day=31)

        dsObs = xr.open_dataset(fileName)
        dsObs.rename({'time': 'Time', 'SST': 'sst'}, inplace=True)
        dsObs = dsObs.sel(Time=slice(timeStart, timeEnd))
        dsObs.coords['month'] = dsObs['Time.month']
        dsObs.coords['year'] = dsObs['Time.year']

        return dsObs  # }}}

    # }}}

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python