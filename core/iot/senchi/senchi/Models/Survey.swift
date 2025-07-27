//
//  Survey.swift
//  senchi
//
//  Created by Michael Dawes on 2025-07-21.
//
import SwiftUI

struct RiskQuestion: Identifiable, Codable {
    let id = UUID()
    let question: String
    let risk_type: String
    let importance: String
    let rubric: [String: Int]
    let requires_photo: Bool
    let risk_level: String
}

struct LocationRiskResponse: Codable {
    let location_risks: [String: String]
    let questions: [RiskQuestion]
}

struct SurveyAnswer {
    var answer: String? = nil
    var photo: UIImage? = nil
}

struct UserAnswer: Codable {
    let question: String
    let answer: String
    let photos: [String]
}

struct AssessmentResponse: Codable {
    let total_score: Double
    let points_earned: Double
    let points_possible: Double
    let breakdown: [String: RiskBreakdown]
    let recommendations: [Recommendation]
}

struct RiskBreakdown: Codable {
    let earned: Double
    let possible: Double
    let percentage: Double
}

struct Recommendation: Codable {
    let question: String
    let risk_type: String
    let risk_level: String
    let importance: String
    let answer: String
    let points_possible: Double
    let requires_photo: Bool
    let photo_validated: Bool
    let points_earned: Double
    let score_percentage: Double
}

struct Pill: View {
    let text: String
    let color: Color
    var body: some View {
        Text(text)
            .font(.caption)
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(color.opacity(0.15))
            .foregroundColor(color)
            .cornerRadius(12)
    }
}

struct Survey {
    let locationRisks: [String: String]
    let questions: [RiskQuestion]
}
