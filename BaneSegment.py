import os
import datetime
import arcpy
import logging
import json

arcpy.env.overwriteOutput = True

def createFieldsAndFeatureClass():
    input_fc = config["input_feature_class"]
    output_fc = config["output_feature_class"]

    # Add fields to input (for calculation)
    fieldList = [['time', 'Date'], ['air_temperature_2m', 'Double'], ['cloud_area_fraction', 'Double'], ['relative_humidity_2m', 'Double'], ['low_type_cloud_area_fraction', 'Double'], ['high_type_cloud_area_fraction', 'Double'], ['precipitation_amount_acc', 'Double']]
    
    for props in fieldList:
        arcpy.AddField_management(input_fc,  *props)

    # Copy to new feature class, and truncate
    arcpy.Copy_management(input_fc, output_fc)
    arcpy.DeleteFeatures_management(output_fc)


def processFile(netcdf_file, input_fc, input_fc_10, input_fc_1, output_fc, output_fc_10, output_fc_1):

    print(config)
    logging.info("Processing NetCDF :: " + netcdf_file)

    # Get the number of time indexes (normally 66 hours) 
    nc_FP = arcpy.NetCDFFileProperties(netcdf_file)  
    top = nc_FP.getDimensionSize(config["nc_time_dimension"])
    logging.info(str(top) + " time slices...")
    
    time_from_nc = nc_FP.getDimensionValue(config["nc_time_dimension"], 0)
    if len(time_from_nc) == 19:
        start_date = datetime.datetime.strptime(time_from_nc, "%d.%m.%Y %H:%M:%S")
    else:
        start_date = datetime.datetime.strptime(time_from_nc, "%d.%m.%Y")


    # For each time slice
    for i in range(0, top):
        # New time dimension
        dimension_value = config["nc_time_dimension"] + " " + str(i)
        new_time = start_date + datetime.timedelta(hours=i)
        
        logging.info("Processing date: " + new_time.strftime("%d.%m.%Y %H.%M") + " - index " + str(i))

        # Update the time-field on the input data
        date_expr = "datetime.datetime(%s,%s,%s,%s,%s)" % (new_time.year, new_time.month, new_time.day, new_time.hour, new_time.minute)
        arcpy.CalculateField_management(input_fc, "time", date_expr)
        arcpy.CalculateField_management(input_fc_10, "time", date_expr)
        arcpy.CalculateField_management(input_fc_1, "time", date_expr)

        # For each variable
        for variable in ["air_temperature_2m", "cloud_area_fraction", "relative_humidity_2m", "low_type_cloud_area_fraction", "high_type_cloud_area_fraction", "precipitation_amount_acc"]:
            temp_raster = "temp_raster_%s_%s" % (i, variable)
            logging.info("Processing variable %s for date %s " % (variable, new_time))

            # Create the raster for the given time/variable
            arcpy.MakeNetCDFRasterLayer_md(netcdf_file, variable, "x", "y", temp_raster, "#", dimension_value, "BY_INDEX")
            # Calculate the value on the input
            arcpy.AddSurfaceInformation_3d(input_fc, temp_raster, "Z_MEAN", "LINEAR")
            arcpy.AddSurfaceInformation_3d(input_fc_10, temp_raster, "Z_MEAN", "LINEAR")
            arcpy.AddSurfaceInformation_3d(input_fc_1, temp_raster, "Z_MEAN", "LINEAR")
            # Update the correct field
            arcpy.CalculateField_management(input_fc, variable, "!Z_MEAN!", "PYTHON_9.3")
            arcpy.CalculateField_management(input_fc_10, variable, "!Z_MEAN!", "PYTHON_9.3")
            arcpy.CalculateField_management(input_fc_1, variable, "!Z_MEAN!", "PYTHON_9.3")
            
        # Copy features to output fc
        logging.info("Copying output data for date %s" % new_time)
        arcpy.arcpy.Append_management([input_fc], output_fc)
        arcpy.arcpy.Append_management([input_fc_10], output_fc_10)
        arcpy.arcpy.Append_management([input_fc_1], output_fc_1)

def joachim_script():
    try:
        # Read config
        global config
        config = json.load(open("c:/Users/student/Desktop/netCDF/config_bane.json"))

        # Settup logging and log level from config
        logging.basicConfig(filename=config["log_file"], level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %X")
        level = logging.getLevelName(config["log_level"])
        logging.getLogger().setLevel(level)

        arcpy.CheckOutExtension("3D")

        #for input_fc, output_fc in zip(config["input_feature_class"], config["output_feature_class"]):
        input_fc = config["input_feature_class"][0]
        input_fc_10 = config["input_feature_class"][1]
        input_fc_1 = config["input_feature_class"][2]
        output_fc = config["output_feature_class"][0]
        output_fc_10 = config["output_feature_class"][1]
        output_fc_1 = config["output_feature_class"][2]
        # Starting the processing
        logging.info("Starting processing...")

         #createFieldsAndFeatureClass()
        netcdf_file = config["netcdf_file"]     
        processFile(netcdf_file, input_fc, input_fc_10, input_fc_1, output_fc, output_fc_10, output_fc_1)

        logging.info("Done processing...")

    except Exception as e:
        logging.exception(e)

def main():



    try:
        # Read config
        global config
        config = json.load(open("c:/Users/student/Desktop/netCDF/config_bane.json"))

        # Settup logging and log level from config
        logging.basicConfig(filename=config["log_file"], level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %X")
        level = logging.getLevelName(config["log_level"])
        logging.getLogger().setLevel(level)

        arcpy.CheckOutExtension("3D")

        # Starting the processing
        logging.info("Starting processing...")

        #createFieldsAndFeatureClass()

        netcdf_file = config["netcdf_file"]     
        processFile(netcdf_file)


        logging.info("Done processing...")
    except Exception as e:
        logging.exception(e)


if __name__ == "__main__":
    main()