import SimpleITK as sitk
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display
import numpy as np
from matplotlib.widgets import  RectangleSelector
import matplotlib.patches as patches


class PointDataAquisition(object):

    """
    This class provides a GUI for choosing the annotation position in a Dicom image.
    User clicks in a slice and the poition of the click will be retrieved.
    """

    def __init__(self, image, figure_size, window_level=None):
        self.image = image
        self.npa, self.min_intensity, self.max_intensity = self.get_window_level_numpy_array(self.image, window_level)
        self.point_indexes = []

        #figure_size = (self.npa.shape[1], self.npa.shape[2])
        # Create a figure.
        self.fig, self.axes = plt.subplots(1, 1, figsize=figure_size)
        self.axes.axis('off')

        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['bottom'].set_visible(False)
        self.axes.spines['left'].set_visible(False)

        self.axes.yaxis.set_ticks_position('left')
        self.axes.xaxis.set_ticks_position('bottom')

        self.axes.xaxis.set_major_locator(plt.NullLocator())
        self.axes.yaxis.set_major_locator(plt.NullLocator())

        self.axes.get_xaxis().set_ticks([])
        self.axes.get_yaxis().set_ticks([])

        #self.axes.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        #self.axes.margins(0, 0)
        # Connect the mouse button press to the canvas (__call__ method is the invoked callback).
        self.fig.canvas.mpl_connect('button_press_event', self)

        ui = self.create_ui()

        # Display the data and the controls, first time we display the image is outside the "update_display" method
        # as that method relies on the previous zoom factor which doesn't exist yet.
        self.axes.imshow(self.npa[self.slice_slider.value, :, :],
                            cmap=plt.cm.Greys_r)
                            #vmin=self.min_intensity,
                            #vmax=self.max_intensity)
        self.update_display()
        display(ui)

    def create_ui(self):
        # Create the active UI components. Height and width are specified in 'em' units. This is
        # a html size specification, size relative to current font size.
        self.viewing_checkbox = widgets.RadioButtons(description='Interaction mode:',
                                                     options=['edit', 'view'],
                                                     value='edit')

        self.clearlast_button = widgets.Button(description='Clear Last',
                                               width='7em',
                                               height='3em')
        self.clearlast_button.on_click(self.clear_last)

        self.clearall_button = widgets.Button(description='Clear All',
                                              width='7em',
                                              height='3em')
        self.clearall_button.on_click(self.clear_all)

        self.slice_slider = widgets.IntSlider(description='image z slice:',
                                              min=0,
                                              max=self.npa.shape[0] - 1,
                                              step=1,
                                              value=int((self.npa.shape[0] - 1) / 2),
                                              width='20em')
        self.slice_slider.observe(self.on_slice_slider_value_change, names='value')

        # Layout of UI components. This is pure ugliness because we are not using a UI toolkit. Layout is done
        # using the box widget and padding so that the visible UI components are spaced nicely.
        bx0 = widgets.Box(padding=7, children=[self.slice_slider])
        bx1 = widgets.Box(padding=7, children=[self.viewing_checkbox])
        bx2 = widgets.Box(padding=15, children=[self.clearlast_button])
        bx3 = widgets.Box(padding=15, children=[self.clearall_button])
        return widgets.HBox(children=[widgets.HBox(children=[bx1, bx2, bx3]), bx0])

    def get_window_level_numpy_array(self, image, window_level):
        npa = sitk.GetArrayViewFromImage(image)
        if not window_level:
            return npa, npa.min(), npa.max()
        else:
            return npa, window_level[1] - window_level[0] / 2.0, window_level[1] + window_level[0] / 2.0

    def on_slice_slider_value_change(self, change):
        self.update_display()

    def update_display(self):
        # We want to keep the zoom factor which was set prior to display, so we log it before
        # clearing the axes.
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()

        # Draw the image and localized points.
        self.axes.clear()
        self.axes.imshow(self.npa[self.slice_slider.value, :, :],
                         cmap=plt.cm.Greys_r)
                         #vmin=self.min_intensity,
                         #vmax=self.max_intensity)
        # Positioning the text is a bit tricky, we position relative to the data coordinate system, but we
        # want to specify the shift in pixels as we are dealing with display. We therefore (a) get the data
        # point in the display coordinate system in pixel units (b) modify the point using pixel offset and
        # transform back to the data coordinate system for display.
        text_x_offset = -10
        text_y_offset = -10
        for i, pnt in enumerate(self.point_indexes):
            if pnt[2] == self.slice_slider.value:
                #self.axes.scatter(pnt[0], pnt[1], s=90, marker='<', color='#00FF00')
                if i == 0:
                    self.axes.annotate("", xy=(pnt[0], pnt[1]), xycoords='data', xytext=(pnt[0]+20, pnt[1]+20), textcoords='data', arrowprops=dict(color='#0BFC2B', arrowstyle="->", connectionstyle="arc3"))
                elif i == 1:
                    self.axes.annotate("", xy=(pnt[0], pnt[1]), xycoords='data', xytext=(pnt[0] + 20, pnt[1] + 20),
                                       textcoords='data',
                                       arrowprops=dict(color='#F7FF00', arrowstyle="->", connectionstyle="arc3"))
                elif i == 2:
                    self.axes.annotate("", xy=(pnt[0], pnt[1]), xycoords='data', xytext=(pnt[0] + 20, pnt[1] + 20),
                                       textcoords='data',
                                       arrowprops=dict(color='#00FFFF', arrowstyle="->", connectionstyle="arc3"))
                elif i == 3:
                    self.axes.annotate("", xy=(pnt[0], pnt[1]), xycoords='data', xytext=(pnt[0] + 20, pnt[1] + 20),
                                       textcoords='data',
                                       arrowprops=dict(color='#FFA200', arrowstyle="->", connectionstyle="arc3"))
                else:
                    self.axes.annotate("", xy=(pnt[0], pnt[1]), xycoords='data', xytext=(pnt[0] + 20, pnt[1] + 20),
                                       textcoords='data',
                                       arrowprops=dict(color='#FF00EF', arrowstyle="->", connectionstyle="arc3"))
                # Get point in pixels.
                text_in_data_coords = self.axes.transData.transform([pnt[0], pnt[1]])
                # Offset in pixels and get in data coordinates.
                text_in_data_coords = self.axes.transData.inverted().transform(
                    (text_in_data_coords[0] + text_x_offset, text_in_data_coords[1] + text_y_offset))
                #self.axes.text(text_in_data_coords[0], text_in_data_coords[1], str(i), color='yellow')
        # self.axes.set_title('You selected {0} points'.format(len(self.point_indexes)))
        self.axes.set_axis_off()
        self.axes.axis('off')

        # Set the zoom factor back to what it was before we cleared the axes, and rendered our data.
        self.axes.set_xlim(xlim)
        self.axes.set_ylim(ylim)


        self.fig.canvas.draw_idle()

    def add_point_indexes(self, point_index_data):
        self.validate_points(point_index_data)
        self.point_indexes.append(list(point_index_data))
        self.update_display()

    def set_point_indexes(self, point_index_data):
        self.validate_points(point_index_data)
        del self.point_indexes[:]
        self.point_indexes = list(point_index_data)
        self.update_display()

    def validate_points(self, point_index_data):
        for p in point_index_data:
            if p[0] >= self.npa.shape[2] or p[0] < 0 or p[1] >= self.npa.shape[1] or p[1] < 0 or p[2] >= self.npa.shape[
                0] or p[2] < 0:
                raise ValueError('Given point (' + ', '.join(map(str, p)) + ') is outside the image bounds.')

    def clear_all(self, button):
        del self.point_indexes[:]
        self.update_display()

    def clear_last(self, button):
        if self.point_indexes:
            self.point_indexes.pop()
            self.update_display()

    def get_points(self):
        return [self.image.TransformContinuousIndexToPhysicalPoint(pnt) for pnt in self.point_indexes]

    def get_point_indexes(self):
        '''
        Return the point indexes, not the continous index we keep.
        '''
        # Round and then cast to int, just rounding will return a float
        return [tuple(map(lambda x: int(round(x)), pnt)) for pnt in self.point_indexes]

    def save_current_image(self, filename):
        self.axes.set_axis_off()
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['bottom'].set_visible(False)
        self.axes.spines['left'].set_visible(False)

        self.axes.yaxis.set_ticks_position('left')
        self.axes.xaxis.set_ticks_position('bottom')

        self.axes.xaxis.set_major_locator(plt.NullLocator())
        self.axes.yaxis.set_major_locator(plt.NullLocator())

        self.axes.get_xaxis().set_ticks([])
        self.axes.get_yaxis().set_ticks([])

        self.fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self.axes.margins(0, 0)

        ext_filename = filename + '.jpg'
        #extent = self.axes.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
        self.fig.savefig(ext_filename, pad_inches=-0.1, bbox_inches='tight')
        img = sitk.ReadImage(ext_filename)
        new_filename = filename + ".dcm"
        sitk.WriteImage(img, new_filename)

    def save_all_images(self, filename, index):

        self.axes.clear()
        self.axes.set_axis_off()
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['bottom'].set_visible(False)
        self.axes.spines['left'].set_visible(False)

        self.axes.yaxis.set_ticks_position('left')
        self.axes.xaxis.set_ticks_position('bottom')

        self.axes.xaxis.set_major_locator(plt.NullLocator())
        self.axes.yaxis.set_major_locator(plt.NullLocator())

        self.axes.get_xaxis().set_ticks([])
        self.axes.get_yaxis().set_ticks([])


        self.fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self.axes.margins(0, 0)
        ext_filename = filename + '.jpg'

        self.axes.imshow(self.npa[index, :, :], cmap=plt.cm.Greys_r)
        self.fig.savefig(ext_filename, pad_inches=-0.1, bbox_inches='tight')
        img = sitk.ReadImage(ext_filename)
        new_filename = filename + ".dcm"
        sitk.WriteImage(img, new_filename)

    def __call__(self, event):
        if self.viewing_checkbox.value == 'edit':
            if event.inaxes == self.axes:
                self.point_indexes.append((event.xdata, event.ydata, self.slice_slider.value))
                self.update_display()