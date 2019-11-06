from sourcextractor.config import *
from glob import glob

# Specify the measurement images
m_imgs = sorted(glob('../input/sim11_[gri]_*.fits'))

# Load the measurement frames
top = load_fits_images(m_imgs)

# The images are on the same level, so we 'split' them based on the FILTER header keyword
top.split(ByKeyword('FILTER'))

# We "freeze" the grouping into a measurement group
# This is done to avoid modifications after measurements have been already
# set.
measurement_group = MeasurementGroup(top)

# For each band
for band, imgs in measurement_group:
    all_apertures = []
    # For each individual image within the band
    for img in imgs:
        # Measure the photometry with apertures of 5, 10 and 20 pixels on the detection frame of reference
        all_apertures.extend(add_aperture_photometry(img, [5, 10, 20]))
    # All apertures for the band, store on the catalog as an array
    add_output_column(f'aperture_{band}', all_apertures)

# Print into stdout the configured output
print_output_columns()
