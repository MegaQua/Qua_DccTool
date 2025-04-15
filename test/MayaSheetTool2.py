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
            self.sheet_names = [sheet.get('properties', {}).get('title', 'Sheet1') for sheet in sheets if
                                sheet.get('properties', {}).get('title') != "デフォルト"]
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

    def read_from_google_sheet(self, *args):
        try:
            # 读取 B 到 L 列的数据
            range_to_read = f"{self.selected_sheet}!B4:L1000"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_to_read
            ).execute()

            values = result.get('values', [])

            if not values:
                print("No data found in the selected sheet.")
                return

            last_b_value = None  # 用于存储 B 列合并单元格的值

            for row_idx, row in enumerate(values, start=4):  # 从第 4 行开始
                if len(row) < 10 or not row[1]:  # 如果 C 列为空，停止读取
                    print(f"Stopping at row {row_idx}, no Name found.")
                    break

                # 处理 B 列合并单元格问题
                b_value = row[0] if len(row) > 0 and row[0] else last_b_value
                if not b_value:
                    print(f"[Row {row_idx}] Warning: Missing value in column B, skipping row.")
                    continue
                last_b_value = b_value  # 更新 B 列的最新非空值

                # C 列的值
                c_value = row[1]  # C 列的 Name
                full_name = f"{b_value}_{c_value}"  # 拼接 B + C 列作为新 Name

                # 解析 ID（去掉最后一个 `_` 及其后面的字符）
                id = full_name.rsplit("_", 1)[0]

                print(f"[Row {row_idx}] Extracted Name: {full_name}, ID: {id}")

                # 获取 TRS 数据（D-L 列）
                try:
                    trs_values = list(map(float, row[2:11]))  # D 到 L 列的 9 个数据
                except ValueError as e:
                    print(f"[Row {row_idx}] Error converting TRS values: {e}, skipping row.")
                    continue

                # 定义 Maya 文件路径
                mb_file_path = f"K:/LO/01_Send_Data/to_Cygames/20250214_BGdataNew/Maya/model/{id}.mb"
                if not os.path.exists(mb_file_path):
                    print(f"[Row {row_idx}] File not found: {mb_file_path}")
                    continue  # 跳过当前行

                # 强制忽略 Maya 版本进行导入
                namespace = full_name
                cmds.file(mb_file_path, i=True, namespace=namespace, ignoreVersion=True)
                print(f"[Row {row_idx}] Imported {mb_file_path} with namespace {namespace}")

                # 获取命名空间中的组对象
                group_name = f"{namespace}:{id}"
                if not cmds.objExists(group_name):
                    print(f"[Row {row_idx}] Group {group_name} not found in scene.")
                    continue  # 跳过当前行

                # 设置 TRS 坐标
                cmds.setAttr(f"{group_name}.translateX", trs_values[0])
                cmds.setAttr(f"{group_name}.translateY", trs_values[1])
                cmds.setAttr(f"{group_name}.translateZ", trs_values[2])

                cmds.setAttr(f"{group_name}.rotateX", trs_values[3])
                cmds.setAttr(f"{group_name}.rotateY", trs_values[4])
                cmds.setAttr(f"{group_name}.rotateZ", trs_values[5])

                cmds.setAttr(f"{group_name}.scaleX", trs_values[6])
                cmds.setAttr(f"{group_name}.scaleY", trs_values[7])
                cmds.setAttr(f"{group_name}.scaleZ", trs_values[8])

                print(f"[Row {row_idx}] Updated {group_name} with TRS values: {trs_values}")

        except HttpError as e:
            print(f"Google Sheets API Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
    def main_window(self):
        if cmds.window("loSheetTool", exists=True):
            cmds.deleteUI("loSheetTool")

        window = cmds.window("loSheetTool", title="LoSheet Tool", widthHeight=(300, 550))
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

        # 添加新按钮：读取 Sheet 数据
        cmds.text(label="4. Read Data from Google Sheet.", parent=top_section)
        cmds.button(label="Read from Google Sheet", command=self.read_from_google_sheet, parent=top_section)

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