# Water leak detection in underground pipe distribution system through satellite imagery and deep learning

This repo contains the code for underground water leak detection in the city of Aguascalientes, Mexico.

The objective is to train Convolutional Neural Network (CNN) capable of classify satellite images from Sentinel-2 into leak or nonleak.  

## Methodology

The methodology of this project follows 3 major steps:

1. Collect and download Sentinel-2 (S2) images based on water leak coordinates.
2. Estimate Land Surface Temperature (LST) with a linear regression model using Landsat 8 (L8) images.
3. Train two CNN models: 1) using S2 spectral bands and estimated LST and 2) using only S2 spectral bands.

## Results

The main results are the followings:

| Model | Category | Recall | Precision | F1-score | 
| ----- | ----- | ----- | ----- | ----- |
| S2 bands and LST | Leak | 0.89 | 0.75 | 0.82 | 
| S2 bands and LST | Non-leak | 0.72 | 0.88 | 0.79 | 
| S2 bands only | Leak | 0.77 | 0.72 | 0.74 | 
| S2 bands only | Non-leak | 0.72 | 0.77 | 0.75 | 

Where S2 bands and LST model got 81% accuracy and S2 bands only model got 74%.

## Code description

To execute the code first you need to create the following data directory structure:

```bash
|-- rs_leaks
    |-- data
    |   |-- clean
    |   |-- images
    |   |-- patches_clean
    |   |   |-- leak
    |   |   |-- non_leak
    |   |-- patches_raw
    |   |   |-- leak
    |   |   |-- non_leak
    |   |-- raw
    |   |-- shp
    |-- src
    |-- models
    |-- figs
```

### Main source files

#### 1. `download_patches` and `download_patches_nonleak`

This two notebooks contain the code to download S2 images and L8 images (that will be used to estimate LST). 

First the coordinate and date of leak repair are used to select the S2 and L8 images. Then a patch is created with a 100 m rectangular buffer which results in a 20 x 20 pixel image. Finally, LST is estimated and added to S2 image as an spectral band, then the patch is downloaded. 

Each notebook can be run indepently to execute the download simultaneusly.

The outputs are the downloaded patches in zip files which are saved in the patches_raw directory, and two csv files containing the metadata of the each downloaded image (like % cloud coverage, days of difference between S2 and L8 images, etc.), those are stored in the clean data subdirectory.

### 2. `preprocess_patches`

This notebook contains the code to unzip the patches and stack them into one single tiff file of dimensions 20 x 20 pixels x 14 channels. The final images are saved in the patches_clean directory.

### 3. `EDA`

The Exploratory Data Analysis is performed in this notebook. Descriptive statistics and miscellaneous figures are shown for leak type distributions, image metadata, sample images, and model performance during training.

### 4. `data_augmentation`

Because only 1970 images were collected, data augmentation techniques are applied to increase dataset size. Simple transformations were applied like rotations, flips, etc. The final dataset is composed by 3909 images.

### 5. `cnn_leaks and cnn_leaks_noLST`

This two notebooks contains the code for model training. Some models with different architectures were tested and those that showed good results were saved in the models directory as well as their corresponding training histories. 

### `leak_data_cleaning`

This notebook is for the cleaning of leak data. Unfortunately, leak data is private and was provided by the water concessionaire of Aguascalientes City.

### `lst_landsat_sentinel`

This is the base code to perform LST estimation. All of this code is used as functions in the `download_patches` `download_patches_nonleak` notebooks.
