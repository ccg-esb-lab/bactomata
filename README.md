# BACTOMATA

**A modular pipeline for plate design, robotic liquid handling, data acquisition, and analysis in microbial experimental evolution**


## Overview

This repository contains the notebooks, source code, example layouts, and technical documentation for BACTOMATA, an open hardware/software pipeline for designing and running microbial experiments in multiwell plates.

BACTOMATA connects plate layout design, OpenTrons robot script generation, BioTek plate-reader data parsing, and Python-based data analysis. The same layout files used to generate robot instructions are reused later to annotate the data, linking each absorbance or fluorescence measurement to the media and bacteria present in each well.

The pipeline is organized around four modules:

- `Bactomata_PlateGenerator`: generates media layouts, bacteria layouts, key dictionaries, and trough layouts.
- `Bactomata_OTscript`: generates OpenTrons OT robot scripts from layout files.
- `Bactomata_DataAcquisition`: acquires absorbance and fluorescence data from BioTek plate readers or an in-house Raspberry Pi-based module.
- `Bactomata_DataAnalysis`: parses raw data, annotates measurements, and produces plots and summary analyses.

## Documentation

The technical documentation is provided as a PDF in [`docs/`](docs/).

The notebooks in [`notebooks/`](notebooks/) implement the main BACTOMATA workflows for plate generation, OpenTrons script generation, data loading, and data analysis.

Example experiment files, including layout files and expected experiment-folder organization, are provided in [`experiments/`](experiments/).

## Repository structure

```text
bactomata/
    layout_widgets.py
    parser.py
    processing.py
    plotter.py

notebooks/
    Bactomata_PlateGenerator.ipynb
    Bactomata_OTscript.ipynb
    Bactomata_DataAnalysis.ipynb

experiments/
    <expeID>/
        raw/
            layouts/
            plate_reader/
        OT_scripts/
        processed/
        figures/
        notes/
```


## Authors
Carles Tardío Pi and Rafael Peña-Miller.

[@Systems Biology Lab, CCG-UNAM](https://github.com/ccg-esb-lab)

## License

[MIT](https://choosealicense.com/licenses/mit/)

This project is licensed under the MIT License - see the [license.txt](license.txt) file for details. Hardware is lincesed under the CERN license.


## Aknowledgements

We thank the help and input from past and present members of the Systems and Synthetic Laboratory at CCG-UNAM.
