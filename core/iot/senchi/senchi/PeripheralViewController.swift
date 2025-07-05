//
//  PerepheralViewController.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-02.
//

import os
import UIKit
import CoreBluetooth

class PeripheralViewController: UIViewController {
    
    @IBOutlet var textView: UITextView!
    @IBOutlet var advertisingSwitch: UISwitch!
    
    var peripheralManager: CBPeripheralManager!

    var transferCharacteristic: CBMutableCharacteristic?
    var connectedCentral: CBCentral?
    var dataToSend = Data()
    var sendDataIndex: Int = 0
    
    override func viewDidLoad() {
        peripheralManager = CBPeripheralManager(delegate: self, queue: nil, options: [CBPeripheralManagerOptionShowPowerAlertKey: true])
        super.viewDidLoad()
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        // Don't keep advertising going while we're not showing.
        peripheralManager.stopAdvertising()

        super.viewWillDisappear(animated)
    }
    
    @IBAction func switchChanged(_ sender: Any) {
        // All we advertise is our service's UUID.
        if advertisingSwitch.isOn {
            peripheralManager.startAdvertising([CBAdvertisementDataServiceUUIDsKey: [TransferService.serviceUUID]])
        } else {
            peripheralManager.stopAdvertising()
        }
    }
    
    static var sendingEOM = false
        
        private func sendData() {
            
            guard let transferCharacteristic = transferCharacteristic else {
                return
            }
            
            // First up, check if we're meant to be sending an EOM
            if PeripheralViewController.sendingEOM {
                // send it
                let didSend = peripheralManager.updateValue("EOM".data(using: .utf8)!, for: transferCharacteristic, onSubscribedCentrals: nil)
                // Did it send?
                if didSend {
                    // It did, so mark it as sent
                    PeripheralViewController.sendingEOM = false
                    os_log("Sent: EOM")
                }
                // It didn't send, so we'll exit and wait for peripheralManagerIsReadyToUpdateSubscribers to call sendData again
                return
            }
            
            // We're not sending an EOM, so we're sending data
            // Is there any left to send?
            if sendDataIndex >= dataToSend.count {
                // No data left.  Do nothing
                return
            }
            
            // There's data left, so send until the callback fails, or we're done.
            var didSend = true
            while didSend {
                
                // Work out how big it should be
                var amountToSend = dataToSend.count - sendDataIndex
                if let mtu = connectedCentral?.maximumUpdateValueLength {
                    amountToSend = min(amountToSend, mtu)
                }
                
                // Copy out the data we want
                let chunk = dataToSend.subdata(in: sendDataIndex..<(sendDataIndex + amountToSend))
                
                // Send it
                didSend = peripheralManager.updateValue(chunk, for: transferCharacteristic, onSubscribedCentrals: nil)
                
                // If it didn't work, drop out and wait for the callback
                if !didSend {
                    return
                }
                
                let stringFromData = String(data: chunk, encoding: .utf8)
                os_log("Sent %d bytes: %s", chunk.count, String(describing: stringFromData))
                
                // It did send, so update our index
                sendDataIndex += amountToSend
                // Was it the last one?
                if sendDataIndex >= dataToSend.count {
                    // It was - send an EOM
                    
                    // Set this so if the send fails, we'll send it next time
                    PeripheralViewController.sendingEOM = true
                    
                    //Send it
                    let eomSent = peripheralManager.updateValue("EOM".data(using: .utf8)!,
                                                                 for: transferCharacteristic, onSubscribedCentrals: nil)
                    
                    if eomSent {
                        // It sent; we're all done
                        PeripheralViewController.sendingEOM = false
                        os_log("Sent: EOM")
                    }
                    return
                }
            }
        }
    
    private func setupPeripheral() {
            
            // Build our service.
            
            // Start with the CBMutableCharacteristic.
            let transferCharacteristic = CBMutableCharacteristic(type: TransferService.characteristicUUID,
                                                             properties: [.notify, .writeWithoutResponse],
                                                             value: nil,
                                                             permissions: [.readable, .writeable])
            
            // Create a service from the characteristic.
            let transferService = CBMutableService(type: TransferService.serviceUUID, primary: true)
            
            // Add the characteristic to the service.
            transferService.characteristics = [transferCharacteristic]
            
            // And add it to the peripheral manager.
            peripheralManager.add(transferService)
            
            // Save the characteristic for later.
            self.transferCharacteristic = transferCharacteristic

        }
}

extension PeripheralViewController: CBPeripheralManagerDelegate {
    
    internal func peripheralManagerDidUpdateState(_ peripheral: CBPeripheralManager) {
            
        advertisingSwitch.isEnabled = peripheral.state == .poweredOn
        
        switch peripheral.state {
        case .poweredOn:
            // ... so start working with the peripheral
            os_log("CBManager is powered on")
            setupPeripheral()
        case .poweredOff:
            os_log("CBManager is not powered on")
            // In a real app, you'd deal with all the states accordingly
            return
        case .resetting:
            os_log("CBManager is resetting")
            // In a real app, you'd deal with all the states accordingly
            return
        case .unauthorized:
            // In a real app, you'd deal with all the states accordingly
            if #available(iOS 13.0, *) {
                switch peripheral.authorization {
                case .denied:
                    os_log("You are not authorized to use Bluetooth")
                case .restricted:
                    os_log("Bluetooth is restricted")
                default:
                    os_log("Unexpected authorization")
                }
            } else {
                // Fallback on earlier versions
            }
            return
        case .unknown:
            os_log("CBManager state is unknown")
            // In a real app, you'd deal with all the states accordingly
            return
        case .unsupported:
            os_log("Bluetooth is not supported on this device")
            // In a real app, you'd deal with all the states accordingly
            return
        @unknown default:
            os_log("A previously unknown peripheral manager state occurred")
            // In a real app, you'd deal with yet unknown cases that might occur in the future
            return
        }
    }
}
