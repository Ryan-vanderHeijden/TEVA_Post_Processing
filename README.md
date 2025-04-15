**Welcome to the TEVA Output Explorer!**

*Python dashboard for viewing and interacting with the outputs of the TEVA algorithm.*

The three main components are:
`main.ipynb` is the main dashboard and manages importing the TEVA output files, running some post-processing functions, setting up plot interactivity, and constructing the dashboard. It it dependent on two supporting files `TEVA_Post_Processing.py` and `TEVA_Dynamic_Plotting.py`.

`TEVA_Post_Processing.py` contains the post-processing functions that transform the .xlsx file output from TEVA into several more informative and user-friendly data structures. These data structures are used to generate the interactive plots.

`TEVA_Dynamic_Plotting.py` contains functions for plotting the various results of the post-processing functions and handling figure updates when the user interacts with the dashboard controls.

Examples of TEVA output files and observation data are included in the `Sample_Data` folder.

**The `main.ipynb` notebook is divided into six sections:**
1. Import dependencies
2. Import TEVA output files and observation data
3. Run post-processing functions
4. Dashboard support
5. Dashboard interactivity
6. Dashboard layout

**The dashboard has five main components:**
1. Controls
    - Minimum and maximum sensitivity sliders
    - CC selector for CC feature subplots
    - "Update" button to update tabbed plots
    - "Save" button to export dashboard as a .html file
2. PPV vs. COV plot
3. CC feature subplots
4. Tabbed plots
    - Feature pairing
    - Features used in CCs
    - CCs used in DNFs
5. Confusion matrix for selected CC

<img src='Sample_Data/Example_Dashboard_Layout.png' width='800'>