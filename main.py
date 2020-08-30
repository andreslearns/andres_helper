from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QGraphicsBlurEffect
from PyQt5.QtCore import QTimer
from networkauto import Ui_MainWindow
from ipaddress import ip_network
from datetime import datetime
from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command, netmiko_send_config
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks.data import load_yaml
from nornir.plugins.tasks.text import template_file
import sys
import os

today = datetime.now()
save_today = today.strftime("%b-%d-%Y")
nr = InitNornir(config_file="config.yml", dry_run=True)
class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, mitigate):
        mitigate = mitigate
        super(MyWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.blur_effect = QGraphicsBlurEffect()
        # MainWindow.setFixedSize(818, 478)
        self.ui.ddosbox.setGeometry(QtCore.QRect(20, 50, 241, 151))
        self.ui.qosbox.setGeometry(QtCore.QRect(20, 50, 241, 151))
        self.ui.dhcp_summary_groupbox.setGeometry(QtCore.QRect(20, 210, 241, 81))
        self.ui.optional_dhcpbox.setGeometry(QtCore.QRect(20, 300 , 241, 81))
        self.ui.qosbox.hide()
        self.ui.dhcpbox.hide()
        self.ui.save_btn.hide()
        self.ui.ddos_netaddrcombobox.hide()
        self.ui.dhcp_summary_groupbox.hide()
        self.ui.optional_dhcpbox.hide()
        self.ui.option_checkbox.hide()

        self.ui.actionQOS.triggered.connect(lambda: self.showqos())
        self.ui.actionDHCP.triggered.connect(lambda: self.showdhcp())
        self.ui.actionDDOS.triggered.connect(lambda: self.showddos())

        # Slider change value for spinbox
        self.ui.dhcp_slider.valueChanged.connect(self.changesubnet)
        self.ui.qos_slider.valueChanged.connect(self.changebandwidth)


        # Buttons links to functions 
        # dhcp
        self.ui.dhcp_generatebtn.clicked.connect(self.dhcpConfig)
        #qos
        self.ui.qos_generatebtn.clicked.connect(self.qosConfig)
        #save
        self.ui.save_btn.clicked.connect(self.saveconfig)

        #ddos mitigation
        self.ui.divert_chkbox.toggled.connect(self.hidecheckboxes)
        self.ui.nodivert_chkbox.toggled.connect(self.hidecheckboxes)
        self.ui.no_divert_all_chkbox.toggled.connect(self.hidecheckboxes)
        self.ui.divert_all_chkbox.toggled.connect(self.hidecheckboxes)
        self.ui.mitigatebtn.hide()
        

        #mitigate button linked to functions
        self.ui.mitigatebtn.clicked.connect(lambda:nr.run(task=self.ddos_automate))
        self.ui.ddos_netaddrcombobox.currentTextChanged.connect(self.hidecheckboxes)

        # combobox datas
        netadd_list = open("inventory/network_addr.cfg").read().splitlines()
        self.ui.ddos_netaddrcombobox.addItems(netadd_list)

        private_ip_lists = open("inventory/private_netaddr.cfg").read().splitlines()
        self.ui.private_addr_cmbox.addItems(private_ip_lists)
        self.ui.private_addr_cmbox.adjustSize()
        
        self.ui.optional_dhcpbox.setEnabled(False)
        self.ui.option_checkbox.toggled.connect(self.showoption)


        self.ui.optional_dhcpbox.setGraphicsEffect(self.blur_effect)
    

    def changesubnet(self):
        subnet = self.ui.dhcp_slider.value()
        self.ui.dhcp_spinbox.setValue(int(subnet))

    def changebandwidth(self):
        bandwidth = self.ui.qos_slider.value()
        self.ui.bw_spinbox.setValue(bandwidth)

    def showqos(self):
        self.ui.qosbox.show()
        self.ui.dhcpbox.hide()
        self.ui.ddosbox.hide()
        self.ui.groupBox.hide()
        self.ui.save_btn.show()
        self.ui.progressBar.hide()
        self.ui.dhcp_summary_groupbox.hide()
        self.ui.optional_dhcpbox.hide()
        self.ui.option_checkbox.hide()
        

    def showdhcp(self):
        self.ui.qosbox.hide()
        self.ui.ddosbox.hide()
        self.ui.dhcpbox.show()
        self.ui.groupBox.hide()
        self.ui.save_btn.show()
        self.ui.progressBar.hide()
        self.ui.dhcp_summary_groupbox.show()
        self.ui.optional_dhcpbox.show()
        self.ui.option_checkbox.show()

    def showddos(self):
        self.ui.ddosbox.show()
        self.ui.qosbox.hide()
        self.ui.dhcpbox.hide()
        self.ui.groupBox.show()
        self.ui.save_btn.hide()
        self.ui.progressBar.show()
        self.ui.progressBar.setValue(0)
        self.ui.dhcp_summary_groupbox.hide()
        self.ui.optional_dhcpbox.hide()
        self.ui.option_checkbox.hide()

    def showoption(self):
        if self.ui.option_checkbox.isChecked():
            self.blur_effect.setEnabled(False)
            self.ui.optional_dhcpbox.setEnabled(True)
            self.ui.optional_dhcpbox.show()
        else:
            self.blur_effect.setEnabled(True)


    def hidecheckboxes(self):
        if self.ui.divert_chkbox.isChecked():
            self.ui.divert_all_chkbox.setEnabled(False)
            self.ui.no_divert_all_chkbox.setEnabled(False)
            self.ui.nodivert_chkbox.setEnabled(False)
            self.ui.ddos_netaddrcombobox.show()
            self.ui.mitigatebtn.show()
            self.mitigate = "divert"
            self.ui.result_label.setText((f"Prefix\t:\t{self.ui.ddos_netaddrcombobox.currentText()}"))
            self.ui.result_label.adjustSize()
            self.ui.task_label.setText(f"Task\t:\tDIVERT")
            self.ui.task_label.adjustSize()

            self.ui.progressBar.setValue(0)


        elif self.ui.nodivert_chkbox.isChecked():
            self.ui.divert_all_chkbox.setEnabled(False)
            self.ui.no_divert_all_chkbox.setEnabled(False)
            self.ui.divert_chkbox.setEnabled(False)
            self.ui.ddos_netaddrcombobox.show()
            self.ui.mitigatebtn.show()
            self.mitigate = "no_divert"
            self.ui.result_label.setText((f"Prefix\t:\t{self.ui.ddos_netaddrcombobox.currentText()}"))
            self.ui.result_label.adjustSize()
            self.ui.task_label.setText(f"Task\t:\tNO DIVERT")
            self.ui.task_label.adjustSize()

            self.ui.progressBar.setValue(0)

        
        elif self.ui.divert_all_chkbox.isChecked():
            self.ui.nodivert_chkbox.setEnabled(False)
            self.ui.no_divert_all_chkbox.setEnabled(False)
            self.ui.divert_chkbox.setEnabled(False)
            self.ui.mitigatebtn.show()
            self.mitigate = "divert_all"
            self.ui.result_label.setText((f"Prefix\t:\t113.61.42.0 - 58.0/24"))
            self.ui.result_label.adjustSize()
            self.ui.task_label.setText(f"Task\t:\tDIVERT ALL")
            self.ui.task_label.adjustSize()

            msg = QMessageBox()
            msg.setWindowTitle("Warning!")
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"Warning! This may affect network stability. use with caution!")
            x = msg.exec_()

            self.ui.progressBar.setValue(0)


        elif self.ui.no_divert_all_chkbox.isChecked():
            self.ui.nodivert_chkbox.setEnabled(False)
            self.ui.divert_all_chkbox.setEnabled(False)
            self.ui.divert_chkbox.setEnabled(False)
            self.ui.mitigatebtn.show()
            self.mitigate = "no_divert_all"
            self.ui.result_label.setText((f"Prefix\t:\t113.61.42 - 58.0/24"))
            self.ui.result_label.adjustSize()
            self.ui.task_label.setText(f"Task\t:\tNO DIVERT ALL")
            self.ui.task_label.adjustSize()
            
            msg = QMessageBox()
            msg.setWindowTitle("Warning!")
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"Warning! This may affect network stability. use with caution!")
            x = msg.exec_()

            self.ui.progressBar.setValue(0)

        else:
            self.ui.no_divert_all_chkbox.setEnabled(True)
            self.ui.nodivert_chkbox.setEnabled(True)
            self.ui.divert_all_chkbox.setEnabled(True)
            self.ui.divert_chkbox.setEnabled(True)
            self.ui.ddos_netaddrcombobox.hide()
            self.ui.mitigatebtn.hide()

    def saveconfig(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()",f"{save_today}.txt","Text Files (*.txt)", options=options)
        try:
            with open(filename[0], 'w') as f:
                my_config = self.ui.output_plaintext.toPlainText()
                f.write(my_config)
        except FileNotFoundError:
            pass

    def dhcpConfig(self):
        self.ui.output_plaintext.clear()
        try:
            officename = self.ui.officenametxt.text()
            officename = officename.upper()

            if not officename:
                raise ValueError("Empty")

            netaddress = self.ui.networkaddresstxt.text()
            mask = self.ui.dhcp_spinbox.value()
            ipnetaddr = f"{netaddress}/{mask}"

            ipnetaddr = ip_network(ipnetaddr)
            netaddress = ipnetaddr[0]
            first_usable = ipnetaddr[1]
            last_usable = ipnetaddr[-2]

            self.ui.output_plaintext.appendPlainText(f"!Generated by: Andres Bukid")

            # private ip address custom
            private_ip = self.ui.private_addr_cmbox.currentText()
            custom_private = private_ip.split(".")
            private_first_octet = custom_private[0]
            private_second_octet = custom_private[1]
            private_address = f"{private_first_octet}.{private_second_octet}."

            usable = []
            for x in ipnetaddr.hosts():
                ipaddr = x
                total_ip = str(ipaddr)
                vlan = str(x)
                vlan = vlan.split(".")
                vlan = str(vlan[3])

                self.ui.output_plaintext.appendPlainText(f"int g0/0/2.{vlan}")
                self.ui.output_plaintext.appendPlainText(f"encapsulation dot1q {vlan}")
                self.ui.output_plaintext.appendPlainText(f"ip address {private_address}{vlan}.254 255.255.255.0")
                self.ui.output_plaintext.appendPlainText(f"ip nat inside\n!")
                self.ui.output_plaintext.appendPlainText(f"ip dhcp pool {officename}_{vlan}")
                self.ui.output_plaintext.appendPlainText(f"network {private_address}{vlan}.0 255.255.255.0")
                self.ui.output_plaintext.appendPlainText(f"default-router {private_address}{vlan}.254")
                self.ui.output_plaintext.appendPlainText(f"dns-server 8.8.8.8 208.67.222.222 208.67.220.220\n!")
                self.ui.output_plaintext.appendPlainText(f"ip dhcp excluded-address {private_address}{vlan}.254\n!")
                self.ui.output_plaintext.appendPlainText(f"ip access-list extended O{officename}_{vlan}")
                self.ui.output_plaintext.appendPlainText(f"permit udp {private_address}{vlan}.0 0.0.0.255 any")
                self.ui.output_plaintext.appendPlainText(f"permit tcp {private_address}{vlan}.0 0.0.0.255 any")
                self.ui.output_plaintext.appendPlainText(f"permit icmp {private_address}{vlan}.0 0.0.0.255 any\n!")
                self.ui.output_plaintext.appendPlainText(f"ip nat pool net{vlan} {ipaddr} {ipaddr} netmask {ipnetaddr.netmask}")
                self.ui.output_plaintext.appendPlainText(f"ip nat inside source list O{officename}_{vlan} pool net{vlan} overload\n!!!!\n")
                
                #progressbar
                usable.append(total_ip)
                cntlen = len(usable)

            # task summary
            self.ui.total_pool_lbl.setText(f"Total Pool\t: {cntlen}")
            self.ui.network_add_lbl.setText(f"Network\t\t: {netaddress}")
            self.ui.netmask_lbl.setText(f"Mask\t\t: {ipnetaddr.netmask}")


        except ValueError:
            msg = QMessageBox()
            msg.setWindowTitle("DHCP Generator")
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Invalid Office Name or Network Address")
            x = msg.exec_()
                
        except ValueError:
                msg = QMessageBox()
                msg.setWindowTitle("DHCP Generator")
                msg.setIcon(QMessageBox.Critical)
                msg.setText(f"Not a Valid Network Address")
                x = msg.exec_()

        except IndexError:
                msg = QMessageBox()
                msg.setWindowTitle("DHCP Generator")
                msg.setIcon(QMessageBox.Critical)
                msg.setText(f"Not a Valid Network Address")
                x = msg.exec_()

    def qosConfig(self):

        try:
            self.ui.output_plaintext.clear()
            policy_name = self.ui.policynametxt.text()
            policy_name = policy_name.upper()
            if not policy_name:
                raise ValueError("Empty")

            bandwidth = self.ui.bw_spinbox.value()

            # ROUTER 
            self.ui.output_plaintext.appendPlainText(f"################[ CISCO-SETUP ]################\n")
            self.ui.output_plaintext.appendPlainText(f"conf t\nclass-map match-all O{policy_name}_limit")
            self.ui.output_plaintext.appendPlainText(f"match any")
            self.ui.output_plaintext.appendPlainText(f"exit\n!")
            self.ui.output_plaintext.appendPlainText(f"policy-map {policy_name}_limit")
            self.ui.output_plaintext.appendPlainText(f"police {bandwidth}000000 conform-action transmit exceed-action drop\n!")

            self.ui.output_plaintext.appendPlainText(f"!!interface Config!!")
            self.ui.output_plaintext.appendPlainText(f"service-policy input {policy_name}_limit")
            self.ui.output_plaintext.appendPlainText(f"service-policy output {policy_name}_limit\nend\n!!!!")
            # SWITCH 
            self.ui.output_plaintext.appendPlainText(f"\n###############[ NON-CISCO-SETUP ]##############\n")
            self.ui.output_plaintext.appendPlainText(f"conf t")
            self.ui.output_plaintext.appendPlainText(f"ip access-list extended O{policy_name}_ACL")
            self.ui.output_plaintext.appendPlainText(f"permit ip any any\n!")
            self.ui.output_plaintext.appendPlainText(f"class-map match-any O{policy_name}_class")
            self.ui.output_plaintext.appendPlainText(f"match access-group name O{policy_name}_ACL\nexit\n!")
            self.ui.output_plaintext.appendPlainText(f"policy-map O{policy_name}_limit")
            self.ui.output_plaintext.appendPlainText(f"class O{policy_name}_class")
            self.ui.output_plaintext.appendPlainText(f"police {bandwidth}000000 conform-action transmit exceed-action drop\nexit\n!")
            self.ui.output_plaintext.appendPlainText(f"!!interface Config!!")
            self.ui.output_plaintext.appendPlainText(f"service-policy input O{policy_name}_limit")
            self.ui.output_plaintext.appendPlainText(f"service-policy output O{policy_name}_limit\nend\n!!!!")

        except ValueError:
                msg = QMessageBox()
                msg.setWindowTitle("Policy name error")
                msg.setIcon(QMessageBox.Critical)
                msg.setText(f"NO Policy Name Detected, Try Again")
                x = msg.exec_()


    def ddos_automate(self, task):
        self.ui.output_plaintext.clear()
        input_ip = self.ui.ddos_netaddrcombobox.currentText()
        net = ip_network(input_ip)
        mitigate = self.mitigate

        # Will send the commands in the routers via netmiko_send_command,[hosts]
        acl_template = task.run(task=template_file,name="Buildling ACL Configuration",
        net=net,
        mitigate=mitigate,
        template="divert.j2", 
        path=f"templates/{task.host}")
        task.host["acl"] = acl_template.result
        acl_output = task.host["acl"]
        acl_send = acl_output.splitlines()
        send_command = task.run(task=netmiko_send_config, name="Pushing ACL Commands", config_commands=acl_send)
        self.ui.output_plaintext.appendPlainText(f"#############{task.host}#############\n")
        self.ui.output_plaintext.appendPlainText(acl_output)
        # print_result(send_command)
        # num_host = len(task.host)

        self.ui.progressBar.setValue(self.ui.progressBar.value() + 50)

def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow(mitigate="")
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15,15,15))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
         
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142,45,197).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)
    main()