#*************************************************************************#
#                                                                         #
#  script INPUT_PARAMETERS                                                #
#                                                                         #
#  list of input parameters needed for the inversion                      #
#                                                                         #
#*************************************************************************#
import numpy as np
import os

### NOTE: do not remove r before strings (r'filename'), to safely use
#         backslashes in filenames

#--------------------------------------------------------------------------
# input file with focal mechnaisms
#--------------------------------------------------------------------------
# input_file = r'../Data/september.dat'
input_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data', 'Input.dat'))
# input_file = r'../Data/20230901__10_100_200.dat'

#--------------------------------------------------------------------------
# output file with results
#--------------------------------------------------------------------------
# output_file = r'../Output/September_Output'
output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Output', 'Output'))

# ASCII file with calculated principal mechanisms
# principal_mechanisms_file = r'../Output/September_principal_mechanisms'
principal_mechanisms_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Output', 'principal_mechanisms'))

#-------------------------------------------------------------------------
# accuracy of focal mechansisms
#--------------------------------------------------------------------------
# number of random noise realizations for estimating the accuracy of the
# solution
N_noise_realizations = 100
# =============================================================================
# 
# estimate of noise in the focal mechanisms (in degrees)
# the standard deviation of the normal distribution of
# errors
mean_deviation = 5

#--------------------------------------------------------------------------
# figure files
#--------------------------------------------------------------------------
shape_ratio_plot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'Figures', 'shape_ratio'))
stress_plot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'Figures', 'stress_directions'))
P_T_plot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'Figures', 'P_T_axes'))
Mohr_plot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'Figures', 'Mohr_circles'))
faults_plot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'Figures', 'faults'))

# shape_ratio_plot = r'../Figures/shape_ratio-s'
# stress_plot      = r'../Figures/stress_directions-s'
# P_T_plot         = r'../Figures/P_T_axes-s'
# Mohr_plot        = r'../Figures/Mohr_circles-s'
# faults_plot      = r'../Figures/faults-s'
 
#--------------------------------------------------------------------------
# advanced control parameters (usually not needed to be changed)
#--------------------------------------------------------------------------
# number of iterations of the stress inversion 
N_iterations = 6

# number of initial stres inversions with random choice of faults
N_realizations = 10

# axis of the histogram of the shape ratio
shape_ratio_min = 0
shape_ratio_max = 1
shape_ratio_step = 0.025

shape_ratio_axis = np.arange(shape_ratio_min+0.0125, shape_ratio_max, shape_ratio_step)
 
# interval for friction values
friction_min  = 0.40
friction_max  = 1.00
friction_step = 0.05


#--------------------------------------------------------------------------
# create output directories if needed
all_files = (output_file, shape_ratio_plot, stress_plot, P_T_plot, Mohr_plot, faults_plot)
for f in all_files:
    folder = os.path.dirname(f)
    if not os.path.exists(folder):
        os.makedirs(folder)
