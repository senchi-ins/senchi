import SwiftUI

public struct NoHighlightButtonStyle: ButtonStyle {
    public func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(1.0) // No scale or opacity change
    }
} 