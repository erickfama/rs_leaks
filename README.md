# Detección de fugas de agua a través de imágenes de percepción remota

This repo contains the code for underground water leak detection in the city of Aguascalientes, Mexico.

To execute the code first you need to create the following data directory structute:

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
```

In order to download and preprocess the patches you first need to run the download_patches notebook and then the preprocess_patches notebook.
