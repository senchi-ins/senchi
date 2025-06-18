import React from "react";
import { View, Text, Image } from "react-native";
import { CoverageItemProps } from "./included.types";
import { Colours } from "@/constants/colors";

interface IncludedItemProps {
  item: CoverageItemProps;
  selected?: boolean;
}

const ICON_SIZE = 100;

export default function IncludedItem({ item, selected }: IncludedItemProps) {
  return (
    <View style={{
      padding: 8,
      borderRadius: 8,
      backgroundColor: selected ? '#e0e7ff' : 'transparent',
      borderWidth: selected ? 2 : 0,
      borderColor: selected ? '#4338ca' : 'transparent',
      alignItems: 'center',
      minWidth: 60,
    }}>
        {typeof item.icon === "number" && (
            <Image 
            source={item.icon} 
            style={{ 
                width: ICON_SIZE, 
                height: ICON_SIZE, 
                resizeMode: 'contain', 
                opacity: 1,
                // tintColor: '#000000',
            }} 
            resizeMode="contain"
            />
        )}
        <Text style={{ fontWeight: 'bold', color: selected ? '#4338ca' : '#222', }}>{item.title}</Text>
        <Text style={{ fontSize: 10, color: '#666' }}>{item.description}</Text>
    </View>
  );
}