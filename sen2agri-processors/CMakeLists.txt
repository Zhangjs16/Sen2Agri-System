project(sen2agri-processors)

cmake_minimum_required(VERSION 2.8)

include(CTest)

find_package(OTB REQUIRED)

include(${OTB_USE_FILE})

if (WIN32)
   if ("${CMAKE_CXX_COMPILER_ID}" MATCHES "Clang")
      message("-- Compiler: Clang")
    elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
      message("-- Compiler: GNU")
    elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel")
      message("-- Compiler: Intel")
    elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
      message("-- Compiler: MSVC")
    endif()
endif()

#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -Wextra -Wno-missing-field-initializers -flto -mno-avx -O3")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -Wextra -Wno-missing-field-initializers")

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR})

add_definitions(-DVCL_CAN_STATIC_CONST_INIT_FLOAT=0)

add_subdirectory(Composite)
add_subdirectory(VegetationStatus)
add_subdirectory(CreateFootprint)
add_subdirectory(Common)
add_subdirectory(ContinuousColorMapping)
add_subdirectory(ProductFormatters)
add_subdirectory(ProductReaders)

if (NOT WIN32)
    add_subdirectory(CropType)
    add_subdirectory(CropMask)
    add_subdirectory(DEM-WB)
    add_subdirectory(AgriculturalPractices)
    add_subdirectory(Sen4CAP)
    add_subdirectory(merge-statistics)
endif()

install(FILES ../scripts/sen2agri_common.py
              ../scripts/split_shapefile.py
        DESTINATION usr/lib/python2.7/site-packages/)

install(FILES ../scripts/insert_l2a_product_to_db.py
              ../scripts/delete_site.py
              ../scripts/job_operations.py
              ../sen2agri-ctl/sen2agri-ctl.py
              ../scripts/filter_site_download_tiles.py
              ../scripts/optimize_gtiff.py
              ../scripts/extract-parcels.py
              ../scripts/import-product-details.py
              ../scripts/export-product.py
              ../scripts/export-product-launcher.py
              ../scripts/crop-type-parcels.py
              ../scripts/crop-type-wrapper.py
              ../scripts/crop-diversification.py
              ../scripts/data-preparation.py
              ../scripts/check_shp.py
              ../scripts/merge-sar.py
              ../scripts/s4c_l4c_manual_exec/agric_practices_data_extraction.py
              ../scripts/s4c_l4c_manual_exec/agric_practices_data_extraction.sh
              ../scripts/s4c_l4c_manual_exec/agric_practices_merge_files.py
              ../scripts/s4c_l4c_manual_exec/agric_practices_merge_files.sh
              ../scripts/s4c_l4c_manual_exec/agric_practices_tsa.sh
              ../scripts/s4c_l4c_manual_exec/extract_practices_infos.sh
              ../scripts/s4c_l4c_manual_exec/launch_agric_practices.sh
              ../scripts/s4c_l4c/s4c_l4c_import_config.py
              ../scripts/s4c_l4c/s4c_l4c_import_practice.py
              ../scripts/s4c_l4c/s4c_l4c_export_all_practices.py
              ../scripts/s4c_l4b/s4c_l4b_import_config.py
              ../scripts/import_theia.sh
        DESTINATION usr/bin/
	    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
                    GROUP_READ GROUP_EXECUTE
                    WORLD_READ WORLD_EXECUTE)

install(FILES dist/sen2agri-disable-thp.conf
        DESTINATION usr/lib/tmpfiles.d)

install(FILES dist/50-open-files.conf
        DESTINATION etc/security/limits.d)
