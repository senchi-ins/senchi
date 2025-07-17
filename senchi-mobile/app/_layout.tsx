import { Colours } from "@/constants/colours";
import { Stack } from "expo-router";


export default function RootLayout() {
  return (
    <Stack 
      screenOptions={{
        headerStyle: {
          backgroundColor: Colours.light.background,
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }}/>
    </Stack>
  );
}