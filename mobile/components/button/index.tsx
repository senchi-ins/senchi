import { View, Text, TouchableOpacity, Pressable } from "react-native";
import { ButtonProps } from "./button.types";
import { Colours } from "../../constants/colors";

export default function Button({ text, onPress }: ButtonProps) {

    return (
      <Pressable 
          onPress={onPress}
          style={({ pressed }) => [
            {
              transform: [{ scale: pressed ? 1 : 1.05 }],
              backgroundColor: Colours.light.primary,
              width: "70%",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: 8,
              padding: 14,
              elevation: pressed ? 0 : 2,
              shadowColor: "#000",
              shadowOffset: {
                width: 0,
                height: 2,
              },
              shadowOpacity: pressed ? 0.1 : 0.15,
              shadowRadius: 4,
            },
          ]}
      >
        <Text style={{ 
          color: Colours.light.default_text,
          fontWeight: "bold",
        }}>{text}</Text>
      </Pressable>
    );
}