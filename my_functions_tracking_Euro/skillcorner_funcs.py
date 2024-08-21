import pandas as pd
import json
from datetime import datetime


def list_to_csv(list, path):
    """This function stores a list of dictionaries into a CSV file"""
    pd.DataFrame(list).to_csv(path, index=False)

class SkillCorner:
    fps = 10 # The frame rate of the SkillCorner data
    ball_id = "-1" # ball_id stored in the output CSV files
        
    def load(self, match_id, metadata_file, tracking_file,data_dir):
        """This function loads the skillcorner data from the given file and saves it in the database."""
        
        with open(metadata_file, encoding="utf-8") as f:
            metadata = json.load(f)

        # basic match info
        match = {}
        match["match_id"] = match_id
        match["match_date"] = datetime.strptime(metadata["date_time"], "%Y-%m-%dT%H:%M:%SZ").strftime("%m/%d/%Y %H:%M")
        match["competition"] = metadata["competition_edition"]["competition"]["name"]
        match["season"] = metadata["competition_edition"]["season"]["name"]
        match["home_team"] = metadata["home_team"]["name"]
        match["away_team"] = metadata["away_team"]["name"]
        match["home_score"] = int(metadata["home_team_score"])
        match["away_score"] = int(metadata["away_team_score"])
        match["home_team_jersey_color"] = metadata["home_team_kit"]["jersey_color"]
        match["away_team_jersey_color"] = metadata["away_team_kit"]["jersey_color"]
        match["home_team_number_color"] = metadata["home_team_kit"]["number_color"]
        match["away_team_number_color"] = metadata["away_team_kit"]["number_color"]
        match["home_team_coach"] = f'{metadata["home_team_coach"]["first_name"]} {metadata["home_team_coach"]["last_name"]}'
        match["away_team_coach"] = f'{metadata["away_team_coach"]["first_name"]} {metadata["away_team_coach"]["last_name"]}'
        match["pitch_name"]= metadata["stadium"]["name"]
        match["pitch_length"]=float(metadata["pitch_length"])
        match["pitch_width"]=float(metadata["pitch_width"])
        match["provider"] = "SkillCorner"
        match["fps"] = self.fps
        if metadata["home_team_side"][0] == "left_to_right":
            match["1H"] = metadata["away_team"]["name"]
            match["2H"] = metadata["home_team"]["name"]
        else:
            match["1H"] = metadata["home_team"]["name"]
            match["2H"] = metadata["away_team"]["name"]
        list_to_csv([match], data_dir / f"{match_id}_metadata.csv")

        

        # extracting tracking data

        on_field_object_ids = set()

        tracking_list = []
        visible_area_list = []
        phase_list = []
        base_timestamp = 0
        pre_half = 1
        pre_possesion = None
        start_frame_id = None
        pre_frame_id = None
        with open(tracking_file, "r", encoding="utf-8") as f:
            for line in f:
                json_object = json.loads(line)
                if json_object["player_data"]!=[]:
                    if not start_frame_id:
                        start_frame_id = json_object["frame"]
                        pre_possesion = json_object["possession"]["group"]
                        pre_frame_id = start_frame_id
                    possession = json_object["possession"]["group"]
                    frame_id = json_object["frame"]
                    timestamp = json_object["timestamp"]

                    time_object = datetime.strptime(
                        json_object["timestamp"], "%H:%M:%S.%f"
                    )
                    timestamp = (
                        (time_object.hour * 60 + time_object.minute) * 60
                        + time_object.second
                    ) * 1000 + time_object.microsecond // 1000

                    half = json_object["period"]
                    if half != pre_half:
                        base_timestamp = timestamp

                    frame = {}
                    frame["match_id"] = match_id
                    frame["half"] = half
                    frame["frame_id"] = frame_id # frame_id is unique accross the match
                    frame["timestamp"] = timestamp - base_timestamp # timestamp starts from each half start and is in ms
                    frame["object_id"] = SkillCorner.ball_id
                    frame["x"] = json_object["ball_data"]["x"]
                    frame["y"] = json_object["ball_data"]["y"]
                    frame["z"] = json_object["ball_data"]["z"]
                    frame["extrapolated"] = not json_object["ball_data"]["is_detected"] # Whether this player's coordinates are extrapolated
                    tracking_list.append(frame)

                    # Store the polygon coordinates of the TV broadcast camera view per frame
                    visible_area = {}
                    visible_area["match_id"] = match_id
                    visible_area["frame_id"] = frame_id
                    for key in ['x_top_left', 'y_top_left', 'x_bottom_left', 'y_bottom_left', 'x_bottom_right', 'y_bottom_right', 'x_top_right', 'y_top_right']:
                        visible_area[key] = json_object["image_corners_projection"][key]
                    
                    visible_area_list.append(visible_area)
                    
                    for obj in json_object["player_data"]:
                        if obj["player_id"] not in on_field_object_ids:
                            on_field_object_ids.add(obj["player_id"])
                        frame = {}
                        frame["match_id"] = match_id
                        frame["half"] = half
                        frame["frame_id"] = frame_id # frame_id is unique accross the match
                        frame["timestamp"] = timestamp - base_timestamp # timestamp starts from each half start and is in ms
                        frame["object_id"] = obj["player_id"]
                        frame["x"] = obj["x"]
                        frame["y"] = obj["y"]
                        frame["z"] = 0.0
                        frame["extrapolated"] = not obj["is_detected"]
                        tracking_list.append(frame)

                    
                    pre_half = half
                    
        list_to_csv(tracking_list, data_dir / f"{match_id}_tracking.csv")
        

        list_to_csv(visible_area_list, data_dir / f"{match_id}_visible_area.csv")
        

    

        # Store the lineups and other player-related information
        lineups = []
        for player in metadata["players"]:
            if player["id"] not in on_field_object_ids:
                continue
            lineup = {}
            lineup["match_id"] = match_id
            lineup["team_name"] = metadata["home_team"]["name"] if player["team_id"] == metadata["home_team"]["id"] else metadata["away_team"]["name"]
            lineup["player_id"] = player["id"]
            lineup["player_first_name"] = player["first_name"]
            lineup["player_last_name"] = player["last_name"]
            lineup["player_shirt_number"] = player["number"]
            lineup["player_position"] = player["player_role"]["name"]
            lineup["player_birthdate"] = player["birthday"]
            lineup["start_time"] = player["start_time"]
            lineup["end_time"] = player["end_time"]
            lineup["yellow_card"] = player["yellow_card"]
            lineup["red_card"] = player["red_card"]
            lineup["injured"] = player["injured"]
            lineup["goal"] = player["goal"]
            lineup["own_goal"] = player["own_goal"]
            lineups.append(lineup)
        
        list_to_csv(lineups, data_dir / f"{match_id}_lineup.csv")
        

        