#! /bin/bash


#UNCOMMENT THE DEFINITIONS BELOW IF YO NEED OTHER VALUES

#parameters for BVInputVariableGeneration
#GENERATED_SAMPLES_NO=100

#parameters for ProSailSimulator
SOLAR_ZENITH_ANGLE=58.25911
SENSOR_ZENITH_ANGLE=14.547387
# Computed as PHI_V - 180 - PHI_S
# if (rel_az < -180.0) then rel_az = rel_az + 360.0
# if (rel_az > 180.0) then rel_az = rel_az - 360.0
# PHI_V>-73.809703566</PHI_V>
#<PHI_S>145.43902353</PHI_S>
RELATIVE_AZIMUTH_ANGLE=-133.259322

#parameters for TrainingDataGenerator
#BV_IDX=0
#ADD_REFLS=0
#RED_INDEX=0
#NIR_INDEX=2

#parameters for generating model
#REGRESSION_TYPE="nn"
#BEST_OF=1

#end of USER modif

../../sen2agri-processors/VegetationStatus/TestScripts/lai_retrieve_processing.py --applocation /home/ramona/sen2agri-processors-build --input \
"/mnt/Sen2Agri_DataSets/L2A/Spot5-T5/SouthAfrica/SPOT5_HRG2_XS_20150414_N2A_SouthAfricaD0000B0000/SPOT5_HRG2_XS_20150414_N2A_SouthAfricaD0000B0000.xml" \
--res 0 --t0 20150414 --tend 20150414 --outdir /mnt/output/ramona/LAI_SouthAfrica_monodate --rsrfile /home/ramona/sen2agri/sen2agri-processors/VegetationStatus/otb-bv/data/spot5hrg1.rsr --solarzenith $SOLAR_ZENITH_ANGLE --sensorzenith $SENSOR_ZENITH_ANGLE --relativeazimuth $RELATIVE_AZIMUTH_ANGLE