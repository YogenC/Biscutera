print("\nApp started, may take a few seconds to load...\n")

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import psutil
import subprocess





class Ui_MainWindow(object):
    def __init__(self):
        self.blocked_processes = {}
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")


        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        # Title Label
        self.title_label = QtWidgets.QLabel(self.centralwidget)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setObjectName("title_label")
        self.title_label.setText("Biscute WiFi Limiter")
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        self.verticalLayout.addWidget(self.title_label)


        self.logo_label = QtWidgets.QLabel(self.centralwidget)
        self.logo_label.setGeometry(QtCore.QRect(20, 20, 100, 100))  
        self.logo_label.setObjectName("logo_label")
        pixmap = QtGui.QPixmap("./logo.png")  
        pixmap = pixmap.scaledToWidth(100, QtCore.Qt.SmoothTransformation)  
        self.logo_label.setPixmap(pixmap)
        self.verticalLayout.addWidget(self.logo_label, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)



        self.allowed_label = QtWidgets.QLabel(self.centralwidget)
        self.allowed_label.setAlignment(QtCore.Qt.AlignCenter)
        self.allowed_label.setObjectName("allowed_label")
        self.allowed_label.setText("Allowed Apps")
        self.allowed_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        self.verticalLayout.addWidget(self.allowed_label)

        self.app_tree = QtWidgets.QTreeWidget(self.centralwidget)
        self.app_tree.setObjectName("app_tree")
        self.app_tree.setColumnCount(1)
        self.app_tree.header().setVisible(False)
        self.app_tree.setStyleSheet(
            """
            QTreeWidget#app_tree {
                background-color: #2c2c2c;
                color: white;
            }
            QTreeWidget#app_tree::item {
                background-color: #424242;
                color: white;
            }
            QTreeWidget#app_tree::item:selected {
                background-color: #1e90ff;
                color: white;
            }
            """
        )
        self.verticalLayout.addWidget(self.app_tree)

        self.blocked_label = QtWidgets.QLabel(self.centralwidget)
        self.blocked_label.setAlignment(QtCore.Qt.AlignCenter)
        self.blocked_label.setObjectName("blocked_label")
        self.blocked_label.setText("Blocked Apps")
        self.blocked_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        self.verticalLayout.addWidget(self.blocked_label)

        self.blocked_tree = QtWidgets.QTreeWidget(self.centralwidget)
        self.blocked_tree.setObjectName("blocked_tree")
        self.blocked_tree.setColumnCount(1)
        self.blocked_tree.header().setVisible(False)
        self.blocked_tree.setStyleSheet(
            """
            QTreeWidget#blocked_tree {
                background-color: #2c2c2c;
                color: white;
            }
            QTreeWidget#blocked_tree::item {
                background-color: #424242;
                color: white;
            }
            QTreeWidget#blocked_tree::item:selected {
                background-color: #1e90ff;
                color: white;
            }
            """
        )
        self.verticalLayout.addWidget(self.blocked_tree)


        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setObjectName("button_layout")

        self.limit_button = QtWidgets.QPushButton(self.centralwidget)
        self.limit_button.setObjectName("limit_button")
        self.limit_button.setText("Limit")
        self.limit_button.setStyleSheet("background-color: #d90429; color: white; font-weight: bold;")
        self.limit_button.clicked.connect(self.block_selected_process)
        self.button_layout.addWidget(self.limit_button)
        self.limit_button.setFixedHeight(40)


        self.open_button = QtWidgets.QPushButton(self.centralwidget)
        self.open_button.setObjectName("open_button")
        self.open_button.setText("Open")
        self.open_button.setStyleSheet("background-color: #0d1b2a; color: white; font-weight: bold;")
        self.open_button.clicked.connect(self.allow_selected_process)
        self.button_layout.addWidget(self.open_button)
        self.open_button.setFixedHeight(40)

        self.verticalLayout.addLayout(self.button_layout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.blocked_apps = []

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Biscute WiFi Limiter"))
        self.limit_button.setToolTip(_translate("MainWindow", "Click to limit selected apps"))
        self.open_button.setToolTip(_translate("MainWindow", "Click to allow selected apps"))

        self.centralwidget.setStyleSheet(
            """
            QWidget#centralwidget {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1e1e1e, stop:1 #343434);
            }
            """
        )

        
        self.blocked_pid = {}
        self.blocked_apps = []
        self.blocked_processes = set()

    def get_running_processes(self):
        processes = {}
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                name = proc.info['name']
                exe = proc.info['exe']
                if name not in processes:
                    processes[name] = {'exes': set(), 'pids': []}
                processes[name]['exes'].add(exe)
                processes[name]['pids'].append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes


    def block_selected_process(self):
        selected_items = self.app_tree.selectedItems()
        if selected_items:
            for top_item in selected_items:
                base_name = top_item.text(0)
                pid = int(top_item.text(1).split(': ')[1].split(',')[0])  # Extract the PID
                print(f"Blocking process: {base_name} with PID: {pid}")
                self.blocked_pid[base_name] = pid
                self.block_network_access(pid)  # Block network access
            self.update_blocked_apps_widget()  # Update UI
            
            #Dont change anything here, you'll mess it up
        else:
            QMessageBox.warning(self.centralwidget, "Warning", "Please select a process to block.")

    def update_blocked_apps_widget(self):
        self.blocked_tree.clear()
        for app_name in self.blocked_apps:
            top_level_item = QtWidgets.QTreeWidgetItem(self.blocked_tree)
            top_level_item.setText(0, app_name)


    def allow_selected_process(self):
        selected_items = self.blocked_tree.selectedItems()
        if selected_items:
            top_item = selected_items[0]
            base_name = top_item.text(0)
            if base_name in self.blocked_pid:
                pid = self.blocked_pid[base_name]
                self.allow_network_access(pid)

                self.update_blocked_apps_widget()
            else:
                QMessageBox.warning(self.centralwidget, "Warning", f"{base_name} not found in blocked processes.")
        else:
            QMessageBox.warning(self.centralwidget, "Warning", "Please select a process to allow.")
    
    
    def block_network_access(self, pid):
        try:
            rule_name = f"block_pid_{pid}"
            if self.check_firewall_rule_exists(rule_name):
                QMessageBox.warning(self.centralwidget, "Warning", f"Firewall rule '{rule_name}' already exists.")
                return

            proc = psutil.Process(pid)
            exe = proc.exe()
            try:
                command = f'netsh advfirewall firewall add rule name="{rule_name}" dir=out program="{exe}" action=block'
                subprocess.run(command, shell=True, check=True)
            except Exception as e:
                QMessageBox.critical(self.centralwidget, "Error", "Failed to block network access. Are you a root user?")
                return
            
            selected_items = self.app_tree.selectedItems()
            if selected_items:
                for top_item in selected_items:
                    base_name = top_item.text(0)
                    self.blocked_pid[base_name] = pid
                    if base_name not in self.blocked_apps:
                        self.blocked_apps.append(base_name)
                    self.blocked_processes.add(base_name)

            self.blocked_pid[pid] = exe  
            QMessageBox.information(self.centralwidget, "Info", f"Blocked network access for PID: {pid}, Program: {exe}")
        except Exception as e:
            QMessageBox.critical(self.centralwidget, "Error", str(e))

    def allow_network_access(self, pid):
        try:
          
            rule_name = f"block_pid_{pid}"
            try:
                command = f'netsh advfirewall firewall delete rule name="{rule_name}"'
                subprocess.run(command, shell=True, check=True)
            except Exception as e:
                QMessageBox.critical(self.centralwidget, "Error", "Failed to delete firewall rule. Are you a root user?")
                return
            
            selected_items = self.blocked_tree.selectedItems()
            if selected_items:
                top_item = selected_items[0]
                base_name = top_item.text(0)
                if base_name in self.blocked_pid:
                    del self.blocked_pid[base_name]  
                    if base_name in self.blocked_apps:
                        self.blocked_apps.remove(base_name)  
                    self.blocked_processes.remove(base_name)
          
            if pid in self.blocked_pid:
                del self.blocked_pid[pid]
            QMessageBox.information(self.centralwidget, "Info", f"Allowed network access for PID: {pid}")
        except Exception as e:
            QMessageBox.critical(self.centralwidget, "Error", str(e))


    def check_firewall_rule_exists(self, rule_name):
        try:
            command = f'netsh advfirewall firewall show rule name="{rule_name}" > nul 2>&1'
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except Exception as e:
            QMessageBox.critical(self.centralwidget, "Error", str(e))
            return False

    def setup_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.populate_tree)
        self.timer.start(5000)


    def populate_tree(self):
        self.app_tree.clear()
        processes = self.get_running_processes()
        grouped_processes = {}
        
        for name, details in processes.items():
            base_name = name.split('.')[0]
            found_group = False
            
            for key in grouped_processes.keys():
                if key in base_name or base_name in key:
                    grouped_processes[key]['exes'].update(details['exes'])
                    grouped_processes[key]['pids'].extend(details['pids'])
                    found_group = True
                    break
            
            if not found_group:
                grouped_processes[base_name] = {'exes': set(), 'pids': []}
                grouped_processes[base_name]['exes'].update(details['exes'])
                grouped_processes[base_name]['pids'].extend(details['pids'])
        
        for base_name, grouped_details in grouped_processes.items():
            if base_name not in self.blocked_processes:
                top_level_item = QtWidgets.QTreeWidgetItem(self.app_tree)
                top_level_item.setText(0, base_name)
                top_level_item.setText(1, f"PIDs: {', '.join(map(str, grouped_details['pids']))}")
                for exe in grouped_details['exes']:
                    if exe:
                        sub_item = QtWidgets.QTreeWidgetItem(top_level_item)
                        sub_item.setText(0, exe)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.setWindowIcon(QtGui.QIcon('./logo.png'))

    ui.populate_tree()
    ui.setup_timer()
    
    MainWindow.show()
    sys.exit(app.exec_())

