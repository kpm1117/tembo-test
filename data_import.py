import os
from uuid import uuid4
import datetime
import json
import pandas as pd
import firebase_setup

STATIC_PATH = os.path.join(os.getcwd(), "static")
CHARACTER_FILES = [
    "marvel_heroes.csv",
    "marvel_villains.csv"
]
CHARACTER_STATS_FILE = "marvel_stats.csv"

class MarvelCharacterImporter(object):
    def __init__(self, replace_existing=True, source_path=None):
        self.source_path = source_path or STATIC_PATH
        self.errors = []
        self.log_entries = []
        self.replace_existing = replace_existing
    
    def log(self, message, message_type="INFO"):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_entries.append("[{}] <{}> {}".format(now, message_type, message))
        if message_type == "ERROR":
            self.errors.append(message)

    def run(self):
        self.log("begin run")
        data = self.extract()
        data = self.transform(data)
        self.load(data)
        self.log("ETL complete; updating logger")
        if len(self.log_entries) > 0:
            with open(os.path.join(STATIC_PATH, "data_import.log"), "w") as out_file:
                for item in self.log_entries:
                    out_file.write("%s\n" % item)
    
    def extract(self):
        self.log("begin extract")
        data = dict(
            character_sets={},
            character_stats=None
        )
        for file_name in CHARACTER_FILES:
            character_path = os.path.join(self.source_path, file_name)
            data["character_sets"][file_name] = pd.read_csv(character_path)
        stats_path = os.path.join(self.source_path, CHARACTER_STATS_FILE)
        data["character_stats"] = pd.read_csv(stats_path)
        return data

    def transform(self, data):
        df_characters = pd.DataFrame()
        df_stats = data["character_stats"]
        df_stats["metric_id"] = df_stats.apply(
            lambda row: row["metric_id"].replace("_", " ").title().replace(" ", "_").strip(), axis=1
        )
        metric_ids = list(df_stats.metric_id.unique())

        character_dict = {} # Will contain the final payload for the Load function
        
        for file_name, df_partial in data["character_sets"].items(): # Create a single df with all character sets
            category = file_name.replace("marvel_", "").replace(".csv", "").title()
            df_partial["Category"] = category
            df_characters = pd.concat([df_characters, df_partial])
        
        cols = df_characters.columns
        df_characters.columns = [c.title().replace(" ", "_") for c in cols]
        df_characters = df_characters.rename(columns={"Eye": "Eyes"})
        df_characters["First_Appearance"] = df_characters.apply(
            lambda row: self._normalize_date(
                row["First_Appearance"], row["Year"]), axis=1
            )
        df_characters.drop("Year", axis=1, inplace=True )
        string_replacements = {
            "Name": [],
            "Identity": [("no dual identity", "no dual Identity"), ("identity", "")],
            "Align": [("characters", "")],
            "Hair": [("no hair", "no Hair"), ("hair", "")],
            "Eyes": [("eyes", "")],
            "Sex": [("characters", "")],
            "Alive": [("characters", "")],
            "At_Large": []
        }
        for col, replacements in string_replacements.items():
            df_characters[col] = df_characters.apply(
                lambda row: self._normalize_string(
                    row, col, replacements
                ), axis=1
            )
        for i, character_row in df_characters.iterrows():
            character_attributes = character_row.to_dict()
            df_mystats = df_stats[df_stats["entity_id"]==character_row["Id"]]
            character_attributes["Stats"] = {metric_id: {} for metric_id in metric_ids}
            for j, stats_row in df_mystats.iterrows():
                # Subcollection of stats keyed by year (key='null' if year is ""/NaN)
                stat_year = "null" if pd.isnull(stats_row.year) else int(stats_row.year)
                character_attributes["Stats"][stats_row.metric_id][stat_year] = stats_row.value

            character_dict[character_row["Id"]] = character_attributes
        return character_dict

    def load(self, data):
        self.log("begin load")
        character_ref = firebase_setup.db.reference("Characters")
        if self.replace_existing:
            character_ref.set(data)
            return
        for character_id, attributes in data.items():
            this_character_ref = character_ref.child(str(character_id))
            this_character_ref.update(attributes)
        return

    def _normalize_string(self, row, col, replacements):
        val = row[col]
        if pd.isnull(val):
            return ""
        new_r = val.lower()
        for pre, post in replacements:
            new_r = new_r.replace(pre, post)
        return new_r.strip().title()

    def _normalize_date(self, val, yr):
        if pd.isnull(val) and pd.isnull(yr):
            return ""
        try:
            yr = str(int(yr))
            item0, item1 = val.split("-")
            month_part = item0 if item0.isalpha() else item1
            try:
                mo = month_part.title().strip()
                dt = datetime.datetime.strptime("{} {}".format(yr, item0.zfill(2)), "%Y %b")
            except (TypeError, ValueError):
                yr = int(item0)
                yr = str(2000 + yr)
                dt = datetime.datetime.strptime("{} {}".format(yr, item1.zfill(2)), "%Y %b")
            return dt.strftime("%Y-%m")
        except:
            message = "Unable to parse date '{}'".format(str(val))
            message = "Unable to parse date '{}'".format(str(val))
            self.log(message, message_type="ERROR")
            return val
