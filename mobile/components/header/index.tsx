import { View, Text, Image   } from "react-native";
import { Colours } from "../../constants/colors";
import Account from "../account";

export default function Header() {
  return (
    <View
      style={{
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "center",
        padding: 16,
        borderBottomWidth: 1,
        borderColor: Colours.light.border,
        width: "100%",
        marginBottom: 16,
      }}
    >
      <Image 
        source={require('../../assets/company/senchi.png')} 
        style={{
          width: 60,
          height: 20,
          resizeMode: 'contain',
          alignSelf: 'flex-end',
        }}
      />
      <Account name="Senchi" email="hello@senchi.com" phone="1234567890" />
    </View>
  );
}