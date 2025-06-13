import { Colours } from "@/constants/colors";
import { View, Text } from "react-native";
import { AvailableInsuranceTypes } from "./included.types";
import IncludedItem from "./item";
import { included } from "./included";

interface IncludedProps {
  selectedIndex: number;
}

const insuranceTypes = [
  AvailableInsuranceTypes.AUTO,
  AvailableInsuranceTypes.RENTAL,
  AvailableInsuranceTypes.HOME,
];

export default function Included({ selectedIndex }: IncludedProps) {
  // Get the selected insurance type
  const selectedType = insuranceTypes[selectedIndex] || insuranceTypes[0];
  // Get the coverages for the selected type
  const coverages = included[selectedType];

  return (
    <View style={{
      width: '100%',
      paddingHorizontal: 16,
      marginTop: 16,
    }}>
      <Text
        style={{
          fontSize: 16,
          fontFamily: 'Poppins_400Regular',
          fontWeight: 'bold',
          textAlign: 'left',
          color: Colours.light.primary,
        }}
      >{"What's included?"}</Text>
      <View style={{    
        flexDirection: 'row',
        gap: 16,
      }}>
        {Object.entries(coverages).map(([key, coverage]) => (
          <IncludedItem key={key} item={coverage} />
        ))}
      </View>
    </View>
  );
}