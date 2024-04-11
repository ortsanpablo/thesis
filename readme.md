# Time Series Forecasting for Sepsis Prediction Thesis

This repo provides code for:
 - processing the MIMIC-III dataset (mimic-data-preprocessing)
 - obtaining sentence bert and TF-IDF representations of text (mimic_text_representations.ipynb)
 - training forecast models employing STraTS architecture
 - forecasting laboratory, sentence bert embeddings and TF-IDF representations
 - evaluating forecasts

## Requirements

requirements.txt contains the requirements of the environment i used on my laptop.

However, all experiments were conducted on bwUniCluster(https://uc2-jupyter.scc.kit.edu/jhub/hub/spawn), selecting 1 GPU and jupyter/tensorflow JupyterLab-Basemodule. (smart_cond_mod.py is also required on the cluster)

## How to use

#### 1) process MIMIC-III Database

https://mimic.physionet.org/

Download the MIMIC database and unzip the files.

#### 2) Run mimic_events_icu_generation.py and mimic_preprocessed_data_generation.py

This accesses the mimic tables to obtain patient data and text, creates the files 'mimic_iii_events_text.csv', 'mimic_iii_icu_text.csv' and 'mimic_iii_preprocessed_text.pkl'


#### 3) Run mimic_text_representations.ipynb

This computes sentence bert embeddings, reduced to 50 dimensions and TF-IDF representations of the text present in mimic_iii_preprocessed_text.pkl and then produces the three datasets used for training:

 - 'mimic_notext.pkl' contains only laboratory features, preprocessed for STraTS.
 - 'mimic_and_tfidf_for_thesis.pkl' contains laboratory features and TF-IDF features obtained in step 2, preprocessed for STraTS. At every given time text was observed, 50 most useful TF-IDF features are added individually. They are named tfidf:X, where X is a number from 0 to 49.
 - 'mimic_and_sbert_for_thesis.pkl' contains laboratory features and sentence bert embeddings obtained in step 2, preprocessed for STraTS. At every given time text was observed, 50 parts of the pca-reduced sentence bert embedding are added individually. They are named sBert:X, where X is a number from 0 to 49.

#### 4) Training

*pre_train.ipynb files
Models get saved in models folder.

#### 5) Forecasting

*forecasting.ipynb files
Loads trained models and saves forecasts in 'Experiments/unseeded_models/forecasts'

#### 6) Evaluation

Evaluation*.ipynb files
Loads forecasts and computes step error + mean step error.
for graphs: graphs.ipynb
produces graphs of the thesis.

#### 7) Misc
smart_cond_mod.py contains code for old tensorflow version that was used by STraTS and is necessary to run the experiments.