import pandas as pd
import numpy as np
import sklearn as sk
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from shiny import *

app_ui = ui.page_fluid(
    ui.h2({"style": "text-align: center;"}, "Expected Batting Average Predictor"),
    ui.row(
        ui.column(
            12,
            ui.div(
                {"class": "app-col"},
                ui.p(
                    """
                    This is an application that allows you to input a batter's MLBID and receive an expected batting 
                    average based on every ball the batter has hit in the 2023 MLB season.
                    """,
                ),
                ui.p(
                    """
                    A player's MLBID can be found by going to the player's profile on mlb.com and look at the url. The 
                    url will end in "playerId=" followed by 6 digits. These 6 digits are the player's MLBID. Below are 5 
                    popular players' MLBID for you to try.
                    """,
                ),
                ui.p(
                    """
                    Ronald Acuna Jr.: 660670; Marcus Semien: 543760; Lars Nootbaar: 663457; Shohei Ohtani: 660271; Luis 
                    Arraez: 650333.
                    """,
                ),
            ),
        )
    ),
    ui.input_numeric("batterID", "Insert an MLBID:", 0),
    ui.output_text_verbatim("babip"),
)


def server(input, output, session):
    @output
    @render.text
    def babip():
        while not input.batterID():
            return "Awaiting input"
        return predictba(input.batterID())


def predictba(input):
    df = pd.read_csv(Path(__file__).parent / '2023AdjustedRegularSeasonBBE.csv')
    df = df[['player_name', 'batter', 'pitcher', 'launch_speed', 'launch_angle', 'launch_speed_angle', 'zone', 'events']]
    idexists = input in df["batter"].unique()
    # This variable will check if the input is a valid batter's MLBID.
    if idexists:
        atbats = pd.read_csv(Path(__file__).parent / 'ABs and Names.csv')
        df_without = df.drop(df[df['batter'] == input].index)
        # This dataframe stores the information of all batted balls, not including the player that is input, to train
        # the machine-learning models on later.
        playerdf = df.loc[df["batter"] == input]
        # This dataframe stores the batted ball information of the batter that will be predicted on later.
        playerabs = atbats.loc[atbats["batter"] == input]
        playerabs = playerabs['abs'].values[0]
        # This variable stores the number of at bats the batter took in the 2023 MLB season.
        scale = df_without[['launch_speed', 'launch_angle', 'launch_speed_angle', 'zone', 'events']]
        secondscale = playerdf[['launch_speed', 'launch_angle', 'launch_speed_angle', 'zone', 'events']]
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(scale)
        scaled_data = pd.DataFrame(scaled_data, columns=scale.columns)
        scaled_player = scaler.fit_transform(secondscale)
        scaled_player = pd.DataFrame(scaled_player, columns=scale.columns)
        # Both dataframes are scaled so that the predictions are more accurate.
        df_without = scaled_data
        df_without['events'] = df_without['events'].astype(int)
        playerdf = scaled_player
        playerdf['events'] = playerdf['events'].astype(int)
        X = df_without[['launch_speed', 'launch_angle', 'launch_speed_angle', 'zone']]
        y = df_without['events']
        playerX = playerdf[['launch_speed', 'launch_angle', 'launch_speed_angle', 'zone']]
        lr = LogisticRegression(class_weight='balanced')
        lr.fit(X, y);
        # Here the logistic regression model trains itself using the dataframe without the input batter's information.
        y_pred = lr.predict(playerX)
        # Here the logistic regression model predicts upon all batted ball occurences the player has during the season.
        xBA = round(y_pred.sum() / playerabs, 4)
        # This variable takes the predicted outcomes and divides the number of hits by the number of atbats and rounds
        # the expected batting average(xBA) to 4 decimal points.
        return "The player's expected batting average is: {}".format(xBA)
    else:
        # If the input number is not a batter's MLBID, this code is returned to inform the user they need to input a
        # different number.
        return "Input is not a batter's MLBID."


app = App(app_ui, server, debug=True)
