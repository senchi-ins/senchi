//
//  ext.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-24.
//

extension String {
    func base64URLToBase64() -> String {
        var base64 = self
            .replacingOccurrences(of: "-", with: "+")
            .replacingOccurrences(of: "_", with: "/")
        let padding = 4 - base64.count % 4
        if padding < 4 {
            base64 += String(repeating: "=", count: padding)
        }
        return base64
    }
}
