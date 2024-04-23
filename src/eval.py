"""
This script computes evaluation metrics for election model outputs.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error


def get_winner(biden_votes, trump_votes):
    """
    Given election results, this function codes whether Trump or Biden won a state.
    :param biden_votes: Electoral college votes for Biden.
    :type biden_votes: int
    :param trump_votes: Electoral college votes for Trump.
    :type trump_votes: int
    :return: True if the winner was Trump, False otherwise.
    :rtype: bool
    """
    if biden_votes > trump_votes:
        return 0
    else:
        return 1


def calc_mse_margin(state_outcomes, y_true, y_pred):
    """
    Calculates the Mean Squared Error between actual and predicted election results for each state.
    :param state_outcomes: Dataframe containing election outcomes, true and predicted, for each state.
    :type state_outcomes: pandas dataframe
    :param y_true: Column containing actual margins for the election results.
    :type y_true: str
    :param y_pred: Column containing predicted margins for the election results.
    :type y_pred: str
    :return: Dataframe enriched with MSE.
    :rtype: pandas dataframe
    """
    mse = mean_squared_error(state_outcomes[y_true], state_outcomes[y_pred])
    # state_outcomes["mse"] = state_outcomes.apply(
    #     lambda x: mean_squared_error([x[y_true]], [x[y_pred]]), axis=1
    # )
    return mse


# Load actual data

# With margins
actual_margin = pd.read_html(
    "https://en.wikipedia.org/wiki/2020_United_States_presidential_election#Results_by_state"
)

m1 = actual_margin[29]["State or district"]
m2 = actual_margin[29]["Margin"]
clean_margin = pd.concat([m1, m2], axis=1)
clean_margin.to_csv("../output/actual_margin.csv")

# Due to non-standard state abbreviations and limited data, manual editing of the Wiki-retrieved data was more efficient
# than using code, resulting in the actual_margin_result.csv file
cleaned_actual_margin = pd.read_csv("../data/2020_election/actual_margin_result.csv")
cleaned_actual_margin["%"] = (
    cleaned_actual_margin["%"].str.strip("%").astype(float) / 100
)

# Electoral college results
actual_2020 = pd.read_csv("../data/2020_election/2020_electoral_results.csv")

# Load predictions with margins
margin_mrp = pd.read_csv("../data/2020_election/margin_final_pred_elec_2020_MRP.csv")
margin_ml = pd.read_csv("../data/2020_election/margin_final_pred_elec_ML_2020.csv")

# Join predictions and actual
joined_preds_actual = cleaned_actual_margin.merge(
    margin_mrp[["State", "margin_trump"]], on="State", how="left"
)
joined_preds_actual = joined_preds_actual.merge(
    margin_ml[["State", "margin_trump"]],
    on="State",
    how="left",
    suffixes=("_mrp", "_ml"),
)

# Calculate MSE
# ML MSE
ml_eval = calc_mse_margin(joined_preds_actual, "%", "margin_trump_ml")

# MRP MSE
mrp_eval = calc_mse_margin(joined_preds_actual, "%", "margin_trump_mrp")

# Create MSE evaluation dataframe
model_eval = pd.DataFrame({"ml_mse": [ml_eval], "mrp_mse": [mrp_eval]})

model_eval.to_csv("../output/model_eval.csv", index=False)

# Load predictions
pred_2020 = pd.read_csv("../data/2020_election/final_pred_elec_ML.csv")
fix_pred_2020 = pd.read_csv(
    "../data/2020_election/20240422_final_pred_elec_ML_2020.csv"
)
mrp_pred_2020 = pd.read_csv("../data/2020_election/final_pred_elec_MRP.csv")

actual_2020["actual_winner"] = actual_2020.apply(
    lambda x: get_winner(x["biden"], x["trump"]), axis=1
)

# Populate dataframe with predicted outcomes
actual_2020["pred_winner"] = pred_2020["state_pred"]
actual_2020["fix_pred_winner"] = pred_2020["state_pred"]
actual_2020["mrp_pred_winner"] = mrp_pred_2020["state_pred"]

# Compare predictions with actual outcomes
actual_2020["pred_accuracy"] = (
    actual_2020["actual_winner"] == actual_2020["pred_winner"]
)
actual_2020["fix_pred_accuracy"] = (
    actual_2020["actual_winner"] == actual_2020["fix_pred_winner"]
)
actual_2020["mrp_pred_accuracy"] = (
    actual_2020["actual_winner"] == actual_2020["mrp_pred_winner"]
)

# Remove extraneous rows
actual_2020 = actual_2020.drop([51, 52], axis=0)

# Calculate accuracy
print(np.sum(actual_2020["pred_accuracy"]) / len(actual_2020))
print(np.sum(actual_2020["fix_pred_accuracy"]) / len(actual_2020))
print(np.sum(actual_2020["mrp_pred_accuracy"]) / len(actual_2020))
actual_2020.to_csv("../output/accuracy_outcomes.csv")
