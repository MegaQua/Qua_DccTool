import maya.cmds as cmds
import sys

# 检查 Python 版本并设置路径
maya_python_version = sys.version_info[:3]
if maya_python_version == (3, 7, 7):
    subsyspath = 'S:\\Public\\qiu_yi\\py3716\\Lib\\site-packages'
elif maya_python_version == (3, 10, 8):
    subsyspath = 'S:\\Public\\qiu_yi\\JCQ_Tool\\Lib\\site-packages'
elif maya_python_version == (3, 9, 7):
    subsyspath = 'S:\\Public\\qiu_yi\\py397\\Lib\\site-packages'
sys.path.insert(0, subsyspath)
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class LoSheetTool:

    def __init__(self):
        self.spreadsheet_id = "1Y_at854iz5aqIrGNyynTKwCaonjEIeHrt-437NRpx2U"
        self.selected_objects = []
        self.sheet_names = []
        self.selected_sheet = ""
        self.service = None
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SERVICE_ACCOUNT_FILE = 'S:/Public/qiu_yi/JCQ_Tool/data/project-gomapy-d737ea76a8ff.json'
        self.init_google_service()

    def init_google_service(self):
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
            self.service = build('sheets', 'v4', credentials=creds)
            self.refresh_sheet_names()
        except Exception as e:
            print(f"Failed to initialize Google Sheets API: {str(e)}")

    def refresh_sheet_names(self):
        try:
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            self.sheet_names = [sheet.get('properties', {}).get('title', 'Sheet1') for sheet in sheets if sheet.get('properties', {}).get('title') != "デフォルト"]
            if self.sheet_names:
                self.selected_sheet = self.sheet_names[0]
        except HttpError as e:
            print(f"Google Sheets API Error: {str(e)}")

    def add_new_sheet(self, sheet_name):
        try:
            body = {
                "requests": [
                    {"addSheet": {"properties": {"title": sheet_name}}}
                ]
            }
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            self.refresh_sheet_names()

            menu_items = cmds.optionMenu("sheetMenu", query=True, itemListLong=True)
            if menu_items:
                for item in menu_items:
                    cmds.deleteUI(item)
            for name in self.sheet_names:
                cmds.menuItem(label=name, parent="sheetMenu")
            print(f"Sheet '{sheet_name}' added successfully.")
        except HttpError as e:
            print(f"Google Sheets API Error: {str(e)}")

    def get_trs_values(self):
        object_data = []
        for obj in self.selected_objects:
            translate = [cmds.getAttr(f"{obj}.translateX"), cmds.getAttr(f"{obj}.translateY"), cmds.getAttr(f"{obj}.translateZ")]
            rotate = [cmds.getAttr(f"{obj}.rotateX"), cmds.getAttr(f"{obj}.rotateY"), cmds.getAttr(f"{obj}.rotateZ")]
            scale = [cmds.getAttr(f"{obj}.scaleX"), cmds.getAttr(f"{obj}.scaleY"), cmds.getAttr(f"{obj}.scaleZ")]
            object_name = obj.split(":")[-1]  # Extract name after namespace
            object_data.append({
                "name": object_name,
                "translate": {
                    "x": round(translate[0], 3),
                    "y": round(translate[1], 3),
                    "z": round(translate[2], 3)
                },
                "rotate": {
                    "x": round(rotate[0], 3),
                    "y": round(rotate[1], 3),
                    "z": round(rotate[2], 3)
                },
                "scale": {
                    "x": round(scale[0], 3),
                    "y": round(scale[1], 3),
                    "z": round(scale[2], 3)
                }
            })
        return object_data

    def upload_to_google_sheet(self, object_data):
        try:
            # Append new data starting from C4
            append_body = {
                'values': []
            }
            for obj in object_data:
                append_body['values'].append([
                    obj['name'],
                    obj['translate']['x'], obj['translate']['y'], obj['translate']['z'],
                    obj['rotate']['x'], obj['rotate']['y'], obj['rotate']['z'],
                    obj['scale']['x'], obj['scale']['y'], obj['scale']['z']
                ])

            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.selected_sheet}!C4",
                valueInputOption="RAW",
                body=append_body
            ).execute()
            cmds.confirmDialog(title="Success", message="Data uploaded successfully to Google Sheet.", button="OK")
        except HttpError as e:
            print(f"Google Sheets API Error: {str(e)}")

    def main_window(self):
        if cmds.window("loSheetTool", exists=True):
            cmds.deleteUI("loSheetTool")

        window = cmds.window("loSheetTool", title="LoSheet Tool", widthHeight=(300, 500))
        main_layout = cmds.formLayout()

        top_section = cmds.columnLayout(adjustableColumn=True, parent=main_layout)

        cmds.text(label="1. Select objects in the scene.", parent=top_section)
        cmds.button(label="Add Selected Objects", command=self.add_selected_objects, parent=top_section)

        cmds.text(label="2. Choose a sheet to save data.", parent=top_section)
        sheet_menu = cmds.optionMenu("sheetMenu", label="Sheet:", changeCommand=self.select_sheet, parent=top_section)
        for name in self.sheet_names:
            cmds.menuItem(label=name, parent=sheet_menu)

        cmds.text(label="3. Upload Data to Google Sheet.", parent=top_section)
        cmds.button(label="Upload to Google Sheet", command=self.upload_data_to_sheet, parent=top_section)

        object_list = cmds.textScrollList("objectList", numberOfRows=8, allowMultiSelection=False, append=self.selected_objects, parent=main_layout)

        # Adjust layout with formLayout constraints
        cmds.formLayout(main_layout, edit=True,
                        attachForm=[(top_section, 'top', 5), (top_section, 'left', 5), (top_section, 'right', 5),
                                    (object_list, 'left', 5), (object_list, 'right', 5), (object_list, 'bottom', 5)],
                        attachControl=[(object_list, 'top', 5, top_section)])

        cmds.showWindow(window)

    def add_selected_objects(self, *args):
        self.selected_objects = cmds.ls(orderedSelection=True) or []  # 使用 orderedSelection=True 确保顺序
        cmds.textScrollList("objectList", edit=True, removeAll=True, append=self.selected_objects)

    def select_sheet(self, sheet_name):
        self.selected_sheet = sheet_name

    def add_new_sheet_command(self, *args):
        new_sheet_name = cmds.textFieldButtonGrp("newSheetName", query=True, text=True)
        if new_sheet_name:
            self.add_new_sheet(new_sheet_name)

    def upload_data_to_sheet(self, *args):
        if not self.selected_objects:
            print("No objects selected.")
            return

        object_data = self.get_trs_values()
        self.upload_to_google_sheet(object_data)

# 实例化并运行工具
lo_sheet_tool = LoSheetTool()
lo_sheet_tool.main_window()