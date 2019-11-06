from sourcextractor.config import *
from glob import glob
import numpy as np

# We can pass arguments to the script!
args = Arguments(
    max_iterations=10,
    mag_zeropoint=32.19
)

set_max_iterations(args.max_iterations)

# Specify the measurement images
m_imgs = sorted(glob('../input/sim11_[gri]_*.fits'))
 # And their PSF
m_psf = sorted(glob('../input/sim11_[gri]_*.psf')) 

 # Load the measurement frames
top = load_fits_images(m_imgs, m_psf)

 # The images are on the same level, so we 'split' them based on the FILTER header keyword
top.split(ByKeyword('FILTER'))

 # We "freeze" the grouping into a measurement group
measurement_group = MeasurementGroup(top)

#############################
### COMMON FOR ALL FRAMES ###
#############################

# X and Y, in pixels in the detection image
x, y = get_pos_parameters()

# Parameters for the exponential profile
ratio = FreeParameter(1, Range((0, 10), RangeType.LINEAR))
rad = FreeParameter(lambda o: o.get_radius(), Range(lambda v, o: (.01 * v, 100 * v), RangeType.EXPONENTIAL))
angle = FreeParameter(lambda o: o.get_angle(), Range((-np.pi, np.pi), RangeType.LINEAR))

# Parameters for the Sersic profile
sersic = FreeParameter(2.0, Range((1.0, 7.0), RangeType.LINEAR))
ratio_sersic = FreeParameter(1, Range((0, 10), RangeType.LINEAR))
rad_sersic = FreeParameter(lambda o: o.get_radius(), Range(lambda v, o: (.01 * v, 100 * v), RangeType.EXPONENTIAL))
angle_sersic = FreeParameter(lambda o: o.get_angle(), Range((-np.pi, np.pi), RangeType.LINEAR))

# Add a prior on the sersic profile
sersic0 = 4
nc = DependentParameter(lambda nt: np.exp(nt - sersic0), sersic)
add_prior(nc, 0.0, 1.0)

# Transform to world coordinates
ra, dec, wc_rad, wc_angle, wc_ratio = get_world_parameters(x, y, rad, angle, ratio)

# For each band (group)
for band, group in measurement_group:
    # Flux is fitted once per group
    flux = get_flux_parameter()
    # We want the magnitude too
    mag = DependentParameter(lambda f: -2.5 * np.log10(f) + args.mag_zeropoint, flux)

    # Models to be fitted
    add_model(group, SersicModel(x, y, flux, rad_sersic, ratio_sersic, angle_sersic, sersic))
    add_model(group, ExponentialModel(x, y, flux, rad, ratio, angle))

    # Output columns that depend on the measurement group
    add_output_column(f'mf_flux_{band}', flux)
    add_output_column(f'mf_mag_{band}', mag)


# Output columns that do not depend on the measurement groups
add_output_column('mf_x', x)
add_output_column('mf_y', y)
add_output_column('mf_rad', rad)
add_output_column('mf_angle', angle)
add_output_column('mf_ratio', ratio)
add_output_column('mf_sersic', sersic)
add_output_column('mf_sersic_rad', rad_sersic)
add_output_column('mf_ra', ra)
add_output_column('mf_dec', dec)

# Print information about the configuration
print_model_fitting_info(measurement_group)
print_output_columns()
print('Max. number of iterations: ', args.max_iterations)
