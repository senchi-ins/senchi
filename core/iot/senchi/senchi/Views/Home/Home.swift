//
//  Home.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-11.
//

import SwiftUI


struct HomeView: View {
    var body: some View {
        VStack {
            Spacer()
            Image(systemName: "house.fill")
                .resizable()
                .scaledToFit()
                .frame(width: 64, height: 64)
                .foregroundColor(SenchiColors.senchiBlue)
            Text("Welcome Home!")
                .font(.title)
                .fontWeight(.bold)
                .padding(.top, 16)
            Text("Your HomeGuard device is now connected.")
                .font(.body)
                .foregroundColor(.gray)
                .padding(.top, 4)
            Spacer()
        }
        .padding()
        .background(Color.white)
        .edgesIgnoringSafeArea(.all)
    }
}
