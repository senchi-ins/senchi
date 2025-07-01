//
//  LeakDetectorApp.swift
//  senchi
//
//  Created by Michael Dawes on 2025-06-30.
//

import UIKit


class LeakDetectorApp: UIResponder, UIApplicationDelegate {
    
    var window: UIWindow?
    
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        
        // Create window and set up the main view controller
        window = UIWindow(frame: UIScreen.main.bounds)
        
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        let viewController = storyboard.instantiateViewController(withIdentifier: "BYZ-38-t0r") as! ViewController
        
        window?.rootViewController = viewController
        window?.makeKeyAndVisible()
        
        return true
    }
    
    func applicationWillResignActive(_ application: UIApplication) {
        // Called when the app is about to move from active to inactive state
    }
    
    func applicationDidEnterBackground(_ application: UIApplication) {
        // Called when the app enters the background
    }
    
    func applicationWillEnterForeground(_ application: UIApplication) {
        // Called when the app is about to enter the foreground
    }
    
    func applicationDidBecomeActive(_ application: UIApplication) {
        // Called when the app becomes active
    }
    
    func applicationWillTerminate(_ application: UIApplication) {
        // Called when the app is about to terminate
    }
} 
