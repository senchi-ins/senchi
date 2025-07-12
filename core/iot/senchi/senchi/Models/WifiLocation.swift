
import SwiftUI
import CoreLocation

class LocationPermissionManager: NSObject, ObservableObject, CLLocationManagerDelegate {
    private let locationManager = CLLocationManager()
    @Published var hasLocationPermission = false
    @Published var permissionDenied = false
    
    override init() {
        super.init()
        locationManager.delegate = self
        checkPermissionStatus()
        requestPermissionIfNeeded()
    }
    
    private func requestPermissionIfNeeded() {
        switch locationManager.authorizationStatus {
        case .notDetermined:
            // Automatically request permission - this shows the iOS popup
            locationManager.requestWhenInUseAuthorization()
        case .denied, .restricted:
            permissionDenied = true
        case .authorizedWhenInUse, .authorizedAlways:
            hasLocationPermission = true
        @unknown default:
            break
        }
    }
    
    func openSettings() {
        if let settingsUrl = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(settingsUrl)
        }
    }
    
    private func checkPermissionStatus() {
        hasLocationPermission = locationManager.authorizationStatus == .authorizedWhenInUse ||
                               locationManager.authorizationStatus == .authorizedAlways
        permissionDenied = locationManager.authorizationStatus == .denied ||
                          locationManager.authorizationStatus == .restricted
    }
    
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        checkPermissionStatus()
        if manager.authorizationStatus == .notDetermined {
            requestPermissionIfNeeded()
        }
    }
}
