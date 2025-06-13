import { View, Text, Image, Pressable } from "react-native";
import { Colours } from "../../constants/colors";

type AccountProps = {
  name: string;
  email: string;
  phone: string;
  address?: string;
}

export default function Account({ name, email, phone, address }: AccountProps) {
  return (
    <Pressable
      onPress={() => {
        console.log('Account pressed');
      }}
      style={{
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        width: 30,
        height: 30,
        borderRadius: 25,
        backgroundColor: Colours.light.primary,
      }}
    >
      <Text 
        style={{ 
          color: Colours.light.default_text, 
          fontSize: 18, 
          fontFamily: 'Poppins_400Regular',
          fontWeight: 'bold',
          textAlign: 'center',
          textAlignVertical: 'center',
          lineHeight: 30,
          height: 30,
          width: 30,
          borderRadius: 25,
      }}>
        {name[0]}
      </Text>
    </Pressable>
  );
}