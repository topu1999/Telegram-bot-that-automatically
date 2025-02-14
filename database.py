import json
from typing import List, Dict

class Database:
    def __init__(self, filename: str = "data.json"):
        self.filename = filename
        self.data = self._load_data()
        self.ADMIN_ID = -1002277943928  # Fixed admin ID for broadcasting

    def _load_data(self) -> Dict:
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "users": [],
                "channels": [],
                "groups": [],
                "user_data": {},  # New field for storing user-specific data
                "admins": []  # New field for admin users
            }

    def _save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_user(self, user_id: int):
        if user_id not in self.data["users"]:
            self.data["users"].append(user_id)
            # Initialize user data
            if str(user_id) not in self.data["user_data"]:
                self.data["user_data"][str(user_id)] = {
                    "has_introduced": False
                }
            self._save_data()

    def get_user_data(self, user_id: int) -> Dict:
        return self.data["user_data"].get(str(user_id), {"has_introduced": False})

    def set_user_introduced(self, user_id: int):
        if str(user_id) not in self.data["user_data"]:
            self.data["user_data"][str(user_id)] = {}
        self.data["user_data"][str(user_id)]["has_introduced"] = True
        self._save_data()

    def add_channel(self, channel_id: int):
        if channel_id not in self.data["channels"]:
            self.data["channels"].append(channel_id)
            self._save_data()

    def add_group(self, group_id: int):
        if group_id not in self.data["groups"]:
            self.data["groups"].append(group_id)
            self._save_data()

    def get_all_users(self) -> List[int]:
        return self.data["users"]

    def get_all_channels(self) -> List[int]:
        return self.data["channels"]

    def get_all_groups(self) -> List[int]:
        return self.data["groups"]

    def is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin"""
        return user_id == self.ADMIN_ID  # Only allow the fixed admin ID


    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            "total_users": len(self.data["users"]),
            "total_channels": len(self.data["channels"]),
            "total_groups": len(self.data["groups"]),
            "total_admins": 1  # Always 1 since we have a fixed admin
        }