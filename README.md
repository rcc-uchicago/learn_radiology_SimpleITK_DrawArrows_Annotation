# learn_radiology_SimpleITK_DrawArrows_Annotation
This code was used by a radiologist to draw the labels inside the https://learn-radiology.rcc.uchicago.edu/takecourse/.
* It takes a Dicom image as an input and it outputs the locations (x, y, and z coordinates) of the label (point) inside that image. The poit is the one indicated by the arrow.
Note that z is the slice number.
* Run `annotation_acquisition_location_points.ipynb`
    * this uses SimpleITK library
    * file `ADC pt 18_case_2` contains an example of the coordinates for 3 annotated points.
