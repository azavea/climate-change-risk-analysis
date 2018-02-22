"""
Set up jupyter notebook widgets to run boundary delineation and overlay analysis
  from the notebook with UI elements
"""

import ipywidgets as widgets
from IPython.display import display

from overlay import analysis, boundaries, constants


class boundary_input():
    """
    Inputs to specify a study area boundary
    """

    def __init__(self,
                 geography_type='msa',
                 name='houston',
                 state='N/A'):
        l = widgets.Layout(width='100%', height='30px')
        l1 = widgets.HTML(
            value="Will you be selecting an American Metropolitan Statistical Area ('msa') or a county ('county')")
        self.geography_type = widgets.Dropdown(
            options=['msa', 'county'], value=geography_type, layout=l)
        l2 = widgets.HTML(
            'If searching for an MSA, enter the name of the major city. If searching for a county, enter the name of the county.')
        self.name = widgets.Text(value=name, layout=l)
        l3 = widgets.HTML(
            'If searching for a county, select the state where it is located. Ignore if searching for an MSA.')
        self.state = widgets.Dropdown(
            options=list(constants.STATE_FIPS.keys()), value=state, layout=l)
        # Leave this as a constant for now
        # l4 = widgets.HTML(
        #     'The location where the output shapefile will be located (leave as default)')
        # self.output_directory = widgets.Text(value=output_directory,
        # layout=l)
        self.run = widgets.Button(
            description='CREATE STUDY AREA SHAPEFILE', layout=widgets.Layout(width='100%', height='80px'))

        self.run.on_click(self.handle_button)
        display(l1, self.geography_type, l2,
                self.name, l3, self.state, self.run)

    def handle_button(self, text):
        """
        Create a study area shapefile on click of run button
        """
        boundaries.get_study_area(self.geography_type.value, self.name.value, self.state.value,
                                  constants.BOUNDARY_OUTPUT_DIR)


class overlay_input():
    """
    Specify inputs for 
    """

    def __init__(self,
                 geonotebook,
                 overlay_name='houston',
                 boundary_shp='/home/hadoop/notebooks/data/write/boundaries/houston_msa.shp',
                 input_points='Hospitals',
                 output_points='/home/hadoop/notebooks/data/output/houston_hospitals.shp',
                 sea_url='https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/TX/TX_HGX_slr_data_dist.zip',
                 storm=1):
        l = widgets.Layout(width='100%', height='30px')
        self.geonotebook = geonotebook
        l1 = widgets.HTML(
            value="Enter a name for this overlay layer (e.g. 'houston').")
        self.overlay_name = widgets.Text(value=overlay_name, layout=l)
        l2 = widgets.HTML(
            value='Specify path to study area shapefile or GoeJSON')
        self.boundary_shp = widgets.Text(value=boundary_shp, layout=l)
        l3 = widgets.HTML(
            value='Select one category of health resources to use. You will determine the risk scores at the locations' +
            ' of each of these facilities within your specified study area')
        self.input_points = widgets.Dropdown(options=list(
            constants.HEALTH_RESOURCE_FILES.keys()), value=input_points, layout=l)
        l4 = widgets.HTML(
            value='Specify a category of storm to use in evaluating storm surge risk' +
            ' (<a href="https://www.nhc.noaa.gov/nationalsurge/#datahub">more information about storm surge</a>)')
        self.storm_val = widgets.IntSlider(
            value=storm, min=1, max=5, step=1, layout=l)
        l5 = widgets.HTML(
            value='Go to the <a href="https://coast.noaa.gov/slrdata/">NOAA Sea Level Rise data download site</a>' +
            ' and copy the link to the dataset that covers your study area. Paste it below. If you have not already ' +
            'it may take quite a while to downloaded this dataset id you have not already done so.')
        self.sea_url = widgets.Text(value=sea_url, layout=l)
        # self.storm = widgets.Text(value=storm_file, layout=l)

        self.run = widgets.Button(
            description='RUN OVERLAY ANALYSIS', layout=widgets.Layout(width='100%', height='80px'))

        self.run.on_click(self.handle_button)
        display(l1, self.overlay_name, l2, self.boundary_shp, l3, self.input_points, l4,
                self.storm_val, l5, self.sea_url, self.run)

    def handle_button(self, text):
        """
        Run overlay analysis and add to map
        """
        storm_file = '/home/hadoop/notebooks/data/read/overlay-layers/storm-surge/US_Category{}_MOM_Inundation_HighTide.tif'.format(
            str(self.storm_val.value))
        analysis.overlay_analysis(self.geonotebook,
                                  self.overlay_name.value,
                                  self.boundary_shp.value,
                                  self.input_points.value,
                                  self.sea_url.value,
                                  storm_file,
                                  constants.NATL_FLOOD_SHP)
